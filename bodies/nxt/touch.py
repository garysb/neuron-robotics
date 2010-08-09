import threading
import time
from libs import ttyLinux
import thread_template
import libs.touch

class touchThread (thread_template.ThreadTemplate):
	def __init__(self, t_queues, connects, t_conds, t_locks, t_sema):
		thread_template.ThreadTemplate.__init__(self, t_queues, connects, t_conds, t_locks, t_sema)
		self.t_queues.create('touch')

	# Default instant
	def run(self):
		self.setName('touch')
		self.display('%s:\t\t\tStarting thread' % self.getName(), level=10)

		self.sensor_state			= 1
		# Check the touch sensor is working properly
		self.display('%s:\t\t\tChecking sensor state' % self.getName(), level=25)
		# FIXME: Need to remove the lock around the if statement
		try:
			self.t_locks['nxt'].acquire()
			tmp_state				= libs.touch.state(self.connects['nxt']['con'])
			self.t_locks['nxt'].release()
			if tmp_state:
				self.display('%s:\t\t\tCurrently pressed in' % self.getName(), level=25)
			else:
				self.display('%s:\t\t\tCurrently not pressed' % self.getName(), level=25)
		except:
			self.display('%s:\t\t\tUnable to get sensor state. Closing thread.' % self.getName(), level=10)
			self.close()

		# Check our touch sensor state
		while True:
			self.parse_queue()
			self._poll()
		# All done. Close the thread
		self.display('%s:\t\t\tClosing thread' % self.getName(), level=10)

	# Loop our function to check for a state change
	def _poll(self):
		time.sleep(0.25)
		try:
			self.t_locks['nxt'].acquire()
			tmp_state				= libs.touch.state(self.connects['nxt']['con'])
			self.t_locks['nxt'].release()
			if tmp_state:
				if self.sensor_state == 1:
					return
				else:
					# The state has changed
					self.sensor_state	= 1
					self.display('%s:\t\t\tIN' % self.getName(), level=50)
					return
			else:
				if self.sensor_state == 0:
					return
				else:
					# The state has changed
					self.sensor_state	= 0
					self.display('%s:\t\t\tOUT' % self.getName(), level=50)
					return
		except:
			self.display('%s:\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Parse our input commands
	def parse_command(self, buff):
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v				= buff.split(' ')

		# Parse all touch sensor functions
		if buff_v[0] == 'touch':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Get the touch sensor state
			if buff_v[1] == 'state':
				self.t_queues.put('touch','state',{})
			# Get the touch sensor state continously
			elif buff_v[1] == 'tail':
				self.t_queues.put('touch','tail',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.t_queues.put('touch','set_debug',{'level':buff_v[2]})
				else:
					self.t_queues.put('touch','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	# Get the current touch sensor state
	def state(self):
		print self.sensor_state

	# Keep polling the touch state until an escape char
	def tail(self):
		# Use the ttyLinux module to catch escape key
		try:
			ttyLinux.setSpecial()
			while 1:
				time.sleep(1)
				keys				= ttyLinux.readLookAhead()
				if [keys].__str__() == "[\'\\x1b\']":
					break
				try:
					self.t_locks['nxt'].acquire()
					tmp_state				= libs.touch.state(self.connects['nxt']['con'])
					self.t_locks['nxt'].release()
					if tmp_state:
						if self.sensor_state == 1:
							print "1"
							continue
						else:
							# The state has changed
							self.sensor_state	= 1
							self.display('%s:\t\t\tIN' % self.getName(), level=50)
							print "1"
							continue
					else:
						if self.sensor_state == 0:
							print "0"
							continue
						else:
							# The state has changed
							self.sensor_state	= 0
							self.display('%s:\t\t\tOUT' % self.getName(), level=50)
							print "0"
							continue
				except:
					self.display('%s:\t\t\tUnable to get sensor state' % self.getName(), level=25)
					break
		finally:
			ttyLinux.setNormal()
