import threading
import Queue
import time
import cPickle

import thread_template
from bodies.ld3w import nmea

class gps(thread_template.ThreadTemplate):
	""" Threaded object to send bluetooth messages to the ld3w controller. This
		lets us generate information about our true location within the world.
		We use this information to try keep track of positions that our relative
		data generator gathers. Once we create a map, we get the gps coordinates
		and name the map by the coordinates. When we read a map, we get the gps
		coordinates and try find a map of the location we are in.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('gps')
		self.waypoints										= []
		self.true_heading									= 1

	def run(self):
		""" Our gps loop keeps polling the gps reciever to try get a new reading
			for our location. Once we have a reading, we tell the rest of the
			system.
		"""
		self.setName('gps')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		# Loop in the thread and wait for items in the queue
		while True:
			
			self.parse_queue()
			time.sleep(1)

		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	def parse_command(self, buff):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v											= buff.split(' ')

		# Parse all gps functions
		if buff_v[0] == 'gps':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			if buff_v[1] == 'position':
				print 'getting position'
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('gps','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('gps','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	def get_position(self):
		""" We query the gps device to try get a position. When we have a new
			position, we return it to the caller.
		"""
		try:
			cur_pos											= {}
			cur_pos['type']									= 'NON'
			# Make sure we only use GGA nmea packets
			while cur_pos['type'] != 'GGA':
				self.parse_queue(timeout=1)
				self.s_locks['ld3w'].acquire()
				cur_pos				= nmea.get_data(self.s_connects.bodies['ld3w']['cons'][0]['sock'])
				self.s_locks['ld3w'].release()
				self.display('%s:\t\t\t\tew:%s sn:%s' % (self.getName(), cur_pos['long'], cur_pos['lat']), level=0)
		except:
				self.display('%s:\t\t\t\tUnable to get position' % self.getName(), level=0)

	def _poll(self):
		try:
			# Check the gps module
			self.s_locks['ld3w'].acquire()
			state											= nmea.get_data(self.s_connects.bodies['ld3w']['cons'][0]['sock'])
			self.s_locks['ld3w'].release()

			# Display very detailed information
			self.display('%s:\t\t\t\t%s' % (self.getName(), state), level=75)

			# Display not-so detailed information
			self.display('', level=50)
			self.display('%s:\t\t\t\tType:\t\t\t%s' % (self.getName(), state['type']), level=50)
			if state['type'] == 'GGA':
				self.display('%s:\t\t\t\tLongitude:\t\t%s' % (self.getName(), state['long']), level=50)
				self.display('%s:\t\t\t\tLatitude:\t\t%s' % (self.getName(), state['lat']), level=50)
				self.display('%s:\t\t\t\tQuality:\t\t%s' % (self.getName(), state['quality']), level=50)

			if state['type'] == 'GSA':
				self.display('%s:\t\t\t\tH dilute:\t\t%s' % (self.getName(), state['hdop']), level=50)
				self.display('%s:\t\t\t\tV dilute:\t\t%s' % (self.getName(), state['vdop']), level=50)
				self.display('%s:\t\t\t\tDimentions:\t\t%s' % (self.getName(), state['fix']), level=50)

			if state['type'] == 'GSV':
				self.display('%s:\t\t\t\tSatellites:\t\t%s' % (self.getName(), state['count']), level=50)

			if state['type'] == 'RMC':
				self.display('%s:\t\t\t\tStatus:\t\t\t%s' % (self.getName(), state['status']), level=50)
				self.display('%s:\t\t\t\tSpeed:\t\t\t%s' % (self.getName(), state['speed']), level=50)
				self.display('%s:\t\t\t\tTrack:\t\t\t%s' % (self.getName(), state['track']), level=50)
				self.display('%s:\t\t\t\tLongitude:\t\t%s' % (self.getName(), state['long']), level=50)
				self.display('%s:\t\t\t\tLatitude:\t\t%s' % (self.getName(), state['lat']), level=50)
		except:
			self.display('%s:\t\t\t\tUnable to poll for position' % self.getName(), level=25)
