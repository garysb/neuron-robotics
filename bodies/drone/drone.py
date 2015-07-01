import threading
import Queue
import time
import cPickle

import thread_template
from bodies.drone import libardrone

class drone(thread_template.ThreadTemplate):
	""" Threaded object to send bluetooth messages to the ld3w controller. This
		lets us generate information about our true location within the world.
		We use this information to try keep track of positions that our relative
		data generator gathers. Once we create a map, we get the gps coordinates
		and name the map by the coordinates. When we read a map, we get the gps
		coordinates and try find a map of the location we are in.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('drone')
		self.actions = libardrone.ARDrone()

	def run(self):
		""" Our gps loop keeps polling the gps reciever to try get a new reading
			for our location. Once we have a reading, we tell the rest of the
			system.
		"""
		self.setName('drone')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		# Loop in the thread and wait for items in the queue
		while True:
			self.parse_queue()

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
		if buff_v[0] == 'drone':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			self.display('%s:\t\t\t\tCalling drone command' % self.getName(), level=10)

			# Battery Level
			if buff_v[1] == 'battery':
				self.s_queues.put('drone','battery',{})
			# Takeoff
			elif buff_v[1] == 'takeoff':
				self.s_queues.put('drone','takeoff',{})
			# Land
			elif buff_v[1] == 'land':
				self.s_queues.put('drone','land',{})
			# Hover
			elif buff_v[1] == 'hover':
				self.s_queues.put('drone','hover',{})
			# Help system
			elif buff_v[1] == 'help':
				self.s_queues.put('drone','parse_help',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('drone','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('drone','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	def parse_help(self):
		""" Display help information for using the threads object. These need
			to be returned as a dictionary of options so we can display them
			inside other interfaces.
		"""
		print('\n## drone #####################################')
		print('drone info			\tList the connections')
		print('drone takeoff		\t\t\tAdd a connection')
		print('drone Land			\t\tRemove a connection')

	def battery(self):
		""" We query the gps device to try get a position. When we have a new
			position, we return it to the caller.
		"""
		try:
				self.s_locks['drone'].acquire()
				print self.actions.navdata.get(0, dict()).get('battery', 0)
				self.s_locks['drone'].release()
				#self.display('%s:\t\t\t\tWe have lift off' % self.getName(), level=0)
		except:
				print "unable to get battery level"
				self.display('%s:\t\t\t\tUnable to take off' % self.getName(), level=0)

	def takeoff(self):
		""" We query the gps device to try get a position. When we have a new
			position, we return it to the caller.
		"""
		try:
				self.s_locks['drone'].acquire()
				self.actions.takeoff()
				self.s_locks['drone'].release()
				print "we have lift off"
				self.display('%s:\t\t\t\tWe have lift off' % self.getName(), level=0)
		except:
				print "unable to take off"
				self.display('%s:\t\t\t\tUnable to take off' % self.getName(), level=0)

	def land(self):
		""" We query the gps device to try get a position. When we have a new
			position, we return it to the caller.
		"""
		try:
				self.s_locks['drone'].acquire()
				self.actions.land()
				self.s_locks['drone'].release()
				self.display('%s:\t\t\t\tTouch down' % self.getName(), level=0)
		except:
				self.display('%s:\t\t\t\tUmm, which way is down, Im lost :(' % self.getName(), level=0)
