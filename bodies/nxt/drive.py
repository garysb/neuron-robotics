#!/usr/bin/env python
# Motor control thread

# NOTE: I made and application that runs on the nxt itself. This is to increase
# the precision of the drive and head commands. So below is a list of valid write
# message blocks and their value ranges:
#	4: Tacho limit		- 1-65535.	- This is in degrees or the weel, so 720 would be 2 weel rotations.
#	5: Direction		- 1/2		- 1 is backwards, 2 is forwards.
#	6: Power			- 1-100		- The amount of power to put on the motors.
#	7: Steering			- -100-100	- Control the offset for the two motors.
#	8: Reset			- [a-z]		- Resets the motor and clears the tacho count.

from __future__ import division
from math import ceil, radians, degrees
import threading
import Queue
import time
import cPickle

import thread_template
from physics import polar
from bodies.nxt.nxt.motor import *

class drive(thread_template.ThreadTemplate):
	""" Threaded object to send bluetooth messages to the nxt controller. This
		controls the drive motors to move the nxt from a specific location.
		All movement instructions (fd, bk) are measured in millimeters and are
		relative to the nxt's current position.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('drive')
		self.r												= 0.0	# Radius from origin (in millimeters)
		self.a												= 0.0	# Azimuth from origin (in radians)
		self.t												= 0.0	# Current heading direction (in degrees)
		self.history										= []	# Movement history

	def run(self):
		""" Our run loop checks the drives message queue to see if any actions
			are needed. If it finds a message in the drive queue, it tries to
			run the method listed.
		"""
		self.setName('drive')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		# Loop in the thread and wait for items in the queue
		while 1:
			self.parse_queue()

		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	def parse_command(self, buff):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the drive queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v											= buff.split(' ')

		# Parse all driving functions
		if buff_v[0] == 'drive':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Stop
			if buff_v[1] == 'stop':
				self.s_queues.put('drive','stop',{})
			# Forward
			elif buff_v[1] == 'fd':
				self.s_queues.put('drive','forward',{'millimeters':buff_v[2]})
			# Backward
			elif buff_v[1] == 'bk':
				self.s_queues.put('drive','backward',{'millimeters':buff_v[2]})
			# Left
			elif buff_v[1] == 'sl':
				self.s_queues.put('drive','spin_left',{'degrees':buff_v[2]})
			# Right
			elif buff_v[1] == 'sr':
				self.s_queues.put('drive','spin_right',{'degrees':buff_v[2]})
			# Get the motor states
			elif buff_v[1] == 'state':
				self.s_queues.put('drive','state',{})
			# Get the motor states
			elif buff_v[1] == 'reset':
				self.s_queues.put('drive','reset',{})
			# Get the drive history
			elif buff_v[1] == 'history':
				for i in self.history:
					print i
			elif buff_v[1] == 'position':
				print 'R:%.1fmm A:%.1frad T:%.1frad' % (self.r, self.a, self.t)
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('drive','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('drive','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	def stop(self):
		""" Simply stop the nxt drive motors moving. To do this, we send the
			nxt a bluetooth message into message box 8. This tells the nxt to
			stop moving the motors.
		"""
		# First get our current tacho count from the last movement
		# Now stop the motors
		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(8,'reset')
		self.s_locks['nxt'].release()
		# Now calculate how much of the last movement wasnt completed
		# tell the positioning system to go back by our returned values

	def forward(self, millimeters):
		""" Drive the nxt motors forward by a limited amount. The amount is set
			in millimeters and then converted into tacho counts. This is so if
			we need to specify a tacho limit (in degrees) at a later stage, we
			can.
		"""
		tachos												= ceil(float(millimeters)*4.21)
		#tachos												= millimeters

		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(4,'%s' % tachos)
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(5,'2')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(6,'100')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(7,'0')
		self.s_locks['nxt'].release()
		self.set_position(m_type='f', m_dist=float(millimeters), m_angle=0.0)

	def backward(self, millimeters):
		""" Move the nxt motors backward a set amount. The amount is measured
			in millimeters and converted into tacho counts. This is so if we
			need to specify a tacho limit (in degrees) at a later stage, we can
		"""
		tachos												= ceil(float(millimeters)*4.21)
		#tachos												= millimeters

		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(4,'%s' % tachos)
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(5,'1')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(6,'100')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(7,'0')
		self.s_locks['nxt'].release()
		self.set_position(m_type='b', m_dist=(0.0-float(millimeters)), m_angle=0.0)

	def spin_left(self, degrees):
		""" The spin_left method turns the nxt motors to make the nxt turn on
			its axis. The turn is entered in degrees and this corrisponds to a
			direct turn ratio.
		"""
		tachos												= ceil(float(degrees)*4.4444444444)
		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(4,'%s' % tachos)
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(5,'2')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(6,'100')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(7,'-100')
		self.s_locks['nxt'].release()
		self.set_position(m_type='l', m_dist=0.0, m_angle=float(degrees))

	def spin_right(self, degrees):
		""" The spin_right method turns the nxt motors to make the nxt turn on
			its axis. The turn is entered in degrees and this corrisponds to a
			direct turn ratio.
		"""
		tachos												= ceil(float(degrees)*4.4444444444)
		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(4,'%s' % tachos)
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(5,'2')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(6,'100')
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(7,'100')
		self.s_locks['nxt'].release()
		self.set_position(m_type='r', m_dist=0.0, m_angle=0.0-float(degrees))

	# Get the state of the motors
	def state(self):
		self.s_locks['nxt'].acquire()
		states												= []
		m_a													= Motor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_B)
		m_b													= Motor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_C)

		states.append(m_a.get_output_state())
		states.append(m_b.get_output_state())
		self.s_locks['nxt'].release()
		for i in states:
			print i

	# Reset drive states
	def reset(self):
		self.s_locks['nxt'].acquire()
		self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(8,'reset')
		self.s_locks['nxt'].release()

	def set_position(self, m_type='f', m_dist=500, m_angle=0):
		""" When we are driving around, we need to hold a position relative to
			our starting point. This is unfortunatly not very acurate due to
			wheel slipage. The good news is that it might probably be updated
			on a regular basis by the relative awareness system. That means
			that when the relative system finds an error, it recalculates the
			values and updates this object.
		"""
		movement											= {}
		movement['type']									= m_type
		movement['distance']								= m_dist
		movement['angle']									= m_angle
		self.r,self.a										= polar.add(self.r, self.a, m_dist, radians(m_angle))
		self.t												+= m_angle
		# Reset our angle when over 360
		if self.t >= 360:
			self.t											= self.t % 360
		if self.t <= -360:
			self.t											= self.t % -360

		# Append our movement to the history log
		self.history.append(movement)

	def get_position(self, tell='global', call='set_position'):
		values												= {}
		values['r']											= self.r
		values['a']											= self.a
		values['t']											= radians(self.t)
		self.s_queues.put(tell,call,{'values':cPickle.dumps(values)})
