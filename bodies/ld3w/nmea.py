import math

# get our position from the gps module
def get_data(gps_sock):
	# Fetch a packet of data from the gps device
	packet							= get_packet(gps_sock)

	# The NMEA sentences we're interested in are:
	#  GGA - Global Positioning System Fix Data
	#  GLL - Geographic Position
	#  RMC - GPS Transit Data
	#  GSV - Detailed Satellite data
	#  GSA - Overall Satellite data
	#  VTG - Vector track an Speed over the Ground
	gps_data						= {}
	if packet['type'] == 'GGA':
		gps_data					= parse_gga_data(packet['data'])
	elif packet['type'] == 'GLL':
		gps_data					= parse_gll_data(packet['data'])
	elif packet['type'] == 'RMC':
		gps_data					= parse_rmc_data(packet['data'])
	elif packet['type'] == 'GSV':
		gps_data					= parse_gsv_data(packet['data'], gps_sock=gps_sock)
	elif packet['type'] == 'GSA':
		gps_data					= parse_gsa_data(packet['data'])
	elif packet['type'] == 'VTG':
		gps_data					= parse_vtg_data(packet['data'])
	else:
		# We got a packet we dont know, report it
		print "gps:			Unknown packet type"

	# If we got a data, print it
	if not gps_data == {}:
		return gps_data

# Generate the checksum for some data
# (Checksum is all the data XOR'd, then turned into hex)
def generate_checksum(data):
	csum = 0
	for c in data:
		csum = csum ^ ord(c)
	hex_csum = "%02x" % csum
	return hex_csum.upper()

# Format a NMEA timestamp into something friendly
def format_time(time):
	hh = time[0:2]
	mm = time[2:4]
	ss = time[4:]
	return "%s:%s:%s UTC" % (hh,mm,ss)

# Format a NMEA date into something friendly
def format_date(date):
	months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
	dd = date[0:2]
	mm = date[2:4]
	yy = date[4:6]
	yyyy = int(yy) + 2000
	return "%s %s %d" % (dd, months[(int(mm)-1)], yyyy)

# Get a packet of data from the gps device
def get_packet(gps_sock):
	"""Reads a packet and checks its valid"""

	# Fetch a line of data from the gps device
	rawdata							= ""
	while 1:
		char						= gps_sock.recv(1)
		if not char:
			break
		rawdata						+= char
		if char == "\n":
			break

	# Validate the packet type
	data							= rawdata.strip()
	if not data[0:3] == '$GP':
		print "gps:			No GP start point in packet"
		return {'type':'err'}

	# If it has a checksum, ensure that's correct
	# (Checksum follows *, and is XOR of everything from
	#  the $ to the *, exclusive)
	if data[-3] == '*':
		exp_checksum				= generate_checksum(data[1:-3])
		if not exp_checksum == data[-2:]:
			print "gps:			Invalid checksum %s, expecting %s" % (data[-2:], exp_checksum)
			return {'type':'err'}

		# Strip the checksum
		data						= data[:-3]

	return {'type':data[3:6], 'data':data[7:]}

# Get the location from a GGA sentence
def parse_gga_data(data):
	d = data.split(',')
	ret = {}
	ret['type']						= 'GGA'
	ret['lat']						= "%s%s" % (d[1],d[2])
	ret['long']						= "%s%s" % (d[3],d[4])
	ret['time']						= format_time(d[0])
	ret['quality']					= d[5]
	ret['tracked']					= d[6]
	ret['dilution']					= d[7]
	ret['altitude']					= "%s%s" % (d[8],d[9])
	ret['height']					= "%s%s" % (d[10],d[11])
	return ret

# Get the location from a GLL sentence
def parse_gll_data(data):
	d = data.split(',')
	ret = {}
	ret['type'] = 'GLL'
	ret['lat'] = "%s%s" % (d[0],d[1])
	ret['long'] = "%s%s" % (d[2],d[3])
	ret['time'] = format_time(d[4])
	return ret

# Get the location from a RMC sentence
def parse_rmc_data(data):
	d = data.split(',')
	ret = {}
	ret['type']						= 'RMC'
	ret['lat']						= "%s%s" % (d[2],d[3])
	ret['long']						= "%s%s" % (d[4],d[5])
	ret['time']						= format_time(d[0])
	ret['status']					= d[1]
	ret['speed']					= d[6]
	ret['track']					= d[7]
	ret['magnetic']					= d[9]
	return ret

# Get the satalite info from a GSV sentence. Because the
# GSV data can span multiple packets, we need to include
# the socket connection. We check the sequence total and
# then fetch seq-1 packets to complete the data.
def parse_gsv_data(data, gps_sock):
	d								= data.split(',')
	ret								= {}
	ret['type']						= 'GSV'
	ret['seq_tot']					= d[0]
	ret['count']					= d[2]
	ret['satellites']				= []

	# Fetch the satallites in packet 1
	ret['satellites'].append({'prn':d[3],'elevation':d[4],'azimuth':d[5],'snr':d[6]})
	ret['satellites'].append({'prn':d[7],'elevation':d[8],'azimuth':d[9],'snr':d[10]})
	ret['satellites'].append({'prn':d[11],'elevation':d[12],'azimuth':d[13],'snr':d[14]})
	ret['satellites'].append({'prn':d[15],'elevation':d[16],'azimuth':d[17],'snr':d[18]})

	# Check to make sure we got here on sequence 1, if not
	# discard the data and return an empty dictionary.
	if d[1] != '1':
		return {}

	# Start our loop to get the next sets of data needed
	i								= 2
	while i <= int(d[0]):
		# Connect to the gps and fetch another packet
		packet						= get_packet(gps_sock)
		# Check we have a gsv packet
		if packet['type'] != 'GSV':
			continue

		i							= i + 1
		# split the data on a comma
		s							= []
		s							= data.split(',')
		# Fetch the next satallites
		ret['satellites'].append({'prn':s[3],'elevation':s[4],'azimuth':s[5],'snr':s[6]})
		ret['satellites'].append({'prn':s[7],'elevation':s[8],'azimuth':s[9],'snr':s[10]})
		ret['satellites'].append({'prn':s[11],'elevation':s[12],'azimuth':s[13],'snr':s[14]})
		ret['satellites'].append({'prn':s[15],'elevation':s[16],'azimuth':s[17],'snr':s[18]})

	return ret

# Get the satalite info from a GSA sentence
def parse_gsa_data(data):
	d								= data.split(',')
	ret								= {}
	ret['type']						= 'GSA'
	ret['detection']				= d[0]
	ret['fix']						= d[1]
	ret['sat1']						= d[2]
	ret['sat2']						= d[3]
	ret['sat3']						= d[4]
	ret['sat4']						= d[5]
	ret['sat5']						= d[6]
	ret['sat6']						= d[7]
	ret['sat7']						= d[8]
	ret['sat8']						= d[9]
	ret['sat9']						= d[10]
	ret['sat10']					= d[11]
	ret['sat11']					= d[12]
	ret['sat12']					= d[13]
	ret['pdop']						= d[14]
	ret['hdop']						= d[15]
	ret['vdop']						= d[16]
	return ret

# Get the location from a VTG sentence
def parse_vtg_data(data):
	d								= data.split(',')
	ret								= {}
	ret['type']						= 'VTG'
	# Need to complete this
	return ret

def calc_dist(from_lat_dec,from_long_dec,to_lat_dec,to_long_dec,true_heading=1):
	"""Uses the spherical law of cosines to calculate the distance and bearing between two positions"""

	# For each co-ordinate system we do, what are the A, B and E2 values?
	# List is A, B, E^2 (E^2 calculated after)
	abe_values						= {
		'wgs84': [ 6378137.0, 6356752.3141, -1 ],
		'osgb' : [ 6377563.396, 6356256.91, -1 ],
		'osie' : [ 6377340.189, 6356034.447, -1 ]
	}

	# The earth's radius, in meters, as taken from an average of the WGS84
	#  a and b parameters (should be close enough)
	earths_radius					= (abe_values['wgs84'][0] + abe_values['wgs84'][1]) / 2.0

	# Turn them all into radians
	from_theta						= float(from_lat_dec)  / 360.0 * 2.0 * math.pi
	from_landa						= float(from_long_dec) / 360.0 * 2.0 * math.pi
	to_theta						= float(to_lat_dec)  / 360.0 * 2.0 * math.pi
	to_landa						= float(to_long_dec) / 360.0 * 2.0 * math.pi

	# Calculate the distance from the curent position to the destination
	d								= math.acos (
			math.sin(from_theta) * math.sin(to_theta) +
			math.cos(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
	) * earths_radius

	distance						= d

	#if d > 100000:
	#	distance					= "%4d km" % (d/1000.0)
	#else:
	#	if d < 2000:
	#		distance				= "%4d m" % d
	#	else:
	#		distance				= "%3.02f km" % (d/1000.0)

	# Calculate the bearing needed
	bearing							= math.atan2 (
			math.sin(to_landa-from_landa) * math.cos(to_theta),
			math.cos(from_theta) * math.sin(to_theta) -
			math.sin(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
	)
	bearing							= bearing / 2.0 / math.pi * 360.0

	#if bearing < 0:
	#	bearing						= bearing + 360

	bearing							= "%03d" % bearing
	heading							= "%03d" % float(true_heading)

	return {'distance':distance,'bearing':bearing,'heading':heading}
