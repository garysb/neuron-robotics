#!/usr/bin/env python
# sound sensor thread

import threading
import time
from libs import ttyLinux
import thread_template
import libs.sound

# Reload our dependancies
# FIXME: Need to get this to reload the template and also only reload when we reload the thread (not the first time)
#reload(thread_template)
reload(libs.sound)

class soundThread (thread_template.ThreadTemplate):
	def __init__(self, t_queues, connects, t_conds, t_locks, t_sema):
		thread_template.ThreadTemplate.__init__(self, t_queues, connects, t_conds, t_locks, t_sema)
		self.t_queues.create('sound')

	# Default instant
	def run(self):
		self.setName('sound')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		self.sensor_state			= 0

		# Check the sound sensor is working properly
		self.display('%s:\t\t\t\tChecking sensor state' % self.getName(), level=25)
		try:
			self.t_locks['nxt'].acquire()
			self.display('%s:\t\t\t\t%sdb' % (self.getName(), libs.sound.state(self.connects['nxt']['con'])), level=25)
			self.t_locks['nxt'].release()
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state. Closing thread.' % self.getName(), level=10)
			self.close()

		# Check our sound sensor state
		while True:
			self.parse_queue()
			#self._poll()

		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	# Loop our function to check for a state change
	def _poll(self):
		time.sleep(2)
		try:
			# Poll the sound sensor
			self.t_locks['nxt'].acquire()
			self.sensor_state		= libs.sound.state(self.connects['nxt']['con'])
			self.display('%s:\t\t\t\t%sdb' % (self.getName(), self.sensor_state), level=50)
			self.t_locks['nxt'].release()
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Parse our input commands
	def parse_command(self, buff):
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v				= buff.split(' ')

		# Parse all sound sensor functions
		if buff_v[0] == 'sound':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Get the sound sensor state
			if buff_v[1] == 'state':
				self.t_queues.put('sound','state',{})
			# Get the sound sensor state continously
			elif buff_v[1] == 'tail':
				self.t_queues.put('sound','tail',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.t_queues.put('sound','set_debug',{'level':buff_v[2]})
				else:
					self.t_queues.put('sound','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	# Get the current sound sensor state
	def state(self):
		try:
			# Poll the sound sensor
			self.t_locks['nxt'].acquire()
			self.sensor_state		= libs.sound.state(self.connects['nxt']['con'])
			self.display('%s:\t\t\t\t%sdb' % (self.getName(), self.sensor_state), level=50)
			self.t_locks['nxt'].release()
		except:
			self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Keep polling the sound state until an escape char
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
					tmp_state			= libs.sound.state(self.connects['nxt']['con'])
					self.t_locks['nxt'].release()
					self.sensor_state	= tmp_state
					print tmp_state
				except:
					self.display('%s:\t\t\t\tUnable to get sensor state' % self.getName(), level=25)
					break
		finally:
			ttyLinux.setNormal()
