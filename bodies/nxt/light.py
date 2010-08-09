import threading
import time
from interfaces.console import ttyLinux
import thread_template
from bodies.nxt.nxt.sensor import *

class light(thread_template.ThreadTemplate):
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('light')
		self.light_state									= False

	# Default instant
	def run(self):
		self.setName('light')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		self.sensor_state									= 0

		# Check the light sensor is working properly
		self.display('%s:\t\t\t\tChecking sensor state' % self.getName(), level=25)
		try:
			self.s_locks['nxt'].acquire()
			self.display('%s:\t\t\t\t%slm' % (
				self.getName(),
				LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4, self.light_state).get_sample()), level=25)
			self.s_locks['nxt'].release()
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state. Closing thread.' % self.getName(), level=10)
			self.close()

		# Check our light sensor state
		while True:
			self.parse_queue()
			#self._poll()

		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	# Loop our function to check for a state change
	def _poll(self):
		time.sleep(2)
		try:
			self.s_locks['nxt'].acquire()
			self.sensor_state		= LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4, self.light_state).get_sample()
			self.s_locks['nxt'].release()
			self.display('%s:\t\t\t\t%slm' % (self.getName(),self.sensor_state), level=50)
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Parse our input commands
	def parse_command(self, buff):
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v				= buff.split(' ')

		# Parse all light sensor functions
		if buff_v[0] == 'light':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Get the light sensor state
			if buff_v[1] == 'state':
				self.s_queues.put('light','state',{})
			# Turn the light on
			elif buff_v[1] == 'on':
				self.s_queues.put('light','set_on',{})
			# Turn the light off
			elif buff_v[1] == 'off':
				self.s_queues.put('light','set_off',{})
			# Get the light sensor state continously
			elif buff_v[1] == 'tail':
				self.s_queues.put('light','tail',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('light','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('light','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	# Turn the light on
	def set_on(self):
		self.light_state									= True
		LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4).set_illuminated(True)

	# Turn the light off
	def set_off(self):
		self.light_state									= False
		LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4).set_illuminated(False)

	# Get the current light sensor state
	def state(self):
		try:
			self.s_locks['nxt'].acquire()
			self.sensor_state		= LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4, self.light_state).get_sample()
			self.s_locks['nxt'].release()
			self.display('%s:\t\t\t\t%slm' % (self.getName(),self.sensor_state), level=50)
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Keep polling the light state until an escape char
	def tail(self):
		# Use the ttyLinux module to catch escape key
		try:
			ttyLinux.setSpecial()
			while 1:
				time.sleep(1)
				keys										= ttyLinux.readLookAhead()
				if [keys].__str__() == "[\'\\x1b\']":
					break
				try:
					self.s_locks['nxt'].acquire()
					tmp_state								= LightSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_4, self.light_state).get_sample()
					self.s_locks['nxt'].release()
					self.sensor_state						= tmp_state
					print tmp_state
				except:
					self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)
					break
		finally:
			ttyLinux.setNormal()
