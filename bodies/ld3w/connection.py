import bluetooth

def create(unique='00:02:76:FE:4E:30'):
	# Check we have a valid address to bind to
	if not bluetooth.is_valid_address(unique):
		return {}

	# Find and connect to the lego nxt
	#try:
	if True:
		con													= {}
		con['id']											= unique
		con['sock']											= bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		con['con']											= con['sock'].connect((unique, 1))

	#except:
	#	return {}

	return con
