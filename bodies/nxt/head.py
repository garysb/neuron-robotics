#!/usr/bin/env python
# Head control thread

import threading
import time
import thread_template
from bodies.nxt.nxt.motor import *

class head(thread_template.ThreadTemplate):
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('head')

	# Default instant
	def run (self):
		self.setName('head')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		self.position										= 0
		self.ratio											= 5.5555555555

		# Loop in the thread and wait for items in the queue
		while 1:
			self.parse_queue()
		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	# Parse our input commands
	def parse_command(self, buff):
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v											= buff.split(' ')

		# Parse all driving functions
		if buff_v[0] == 'head':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print 'Position: %s' % self.position
				return

			# Stop
			if buff_v[1] == 'stop':
				self.s_queues.put('head','stop',{})
			# Left
			elif buff_v[1] == 'left':
				# Check we dont get a value over 90 degrees
				if int(buff_v[2]) >= 91:
					print 'My head can only turn 90 degrees to the left'
				else:
					self.s_queues.put('head','left',{'degrees':buff_v[2]})
			# Right
			elif buff_v[1] == 'right':
				# Check we dont get a value over 90 degrees
				if int(buff_v[2]) >= 91:
					print 'My head can only turn 90 degrees to the right'
				else:
					self.s_queues.put('head','right',{'degrees':buff_v[2]})
			# Center
			elif buff_v[1] == 'center':
				self.s_queues.put('head','center',{})
			# Show the head position
			elif buff_v[1] == 'position':
				print self.position
			# Get the motor states
			elif buff_v[1] == 'state':
				self.s_queues.put('head','state',{})
			# Get the motor states
			elif buff_v[1] == 'reset':
				self.s_queues.put('head','reset',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('head','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('head','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	def close(self):
		""" Before we call the thread template close command, make sure that
			our head is in the center position. We dont want to have to try
			move the head by hand every time because thats very annoying.
		"""
		self.center()
		thread_template.ThreadTemplate.close(self)

	# Stop (Stop the head moving)
	def stop(self):
		# Stop our head motor
		m													= Motor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_A)
		m.power												= 0
		m.mode												= MODE_BRAKE
		m.run_state											= RUN_STATE_RUNNING
		m.tacho_limit										= 0
		m.tacho_count										= 0
		m.block_tacho_count									= 0
		m.regulation										= REGULATION_IDLE
		m.turn_ratio										= 0
		m.rotation_count									= 0
		self.s_locks['nxt'].acquire()
		m.set_output_state()
		self.s_locks['nxt'].release()

	# Return to center position (0)
	def center(self):
		print 'gotit'
		# Check if we are already at the center (0) position.
		if self.position == 0:
			return
		# Its to the right. Need to travel left
		elif self.position >= 1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (self.position * self.ratio))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'1')
			self.s_locks['nxt'].release()
		# Its to the left. Need to travel right
		elif self.position <= -1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (self.position * self.ratio * -1))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'2')
			self.s_locks['nxt'].release()

		# Set the position variable to zero
		self.position										= 0

	# Set position of head to be left
	def left(self, degrees):
		degrees												= int(degrees)
		tacho												= int(degrees + self.position)

		# If tacho returns a negative number we need to turn to the right
		if tacho <= -1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (tacho * 5.5555555555 * -1))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'2')
			self.s_locks['nxt'].release()
		elif tacho >= 1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (tacho * 5.5555555555))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'1')
			self.s_locks['nxt'].release()
		else:
			pass

		# Set self.position to the new value
		self.position										= degrees * -1

	# turn our head x degrees to the right
	def right(self, degrees):
		# Although we want the head right, it might actually have to move
		# left. This is because its an absolute movement.
		degrees												= int(degrees)
		tacho												= int(degrees - self.position)

		# If tacho returns a negative number we need to turn to the right
		if tacho <= -1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (tacho * 5.5555555555 * -1))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'1')
			self.s_locks['nxt'].release()
		elif tacho >= 1:
			self.s_locks['nxt'].acquire()
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(2,'%s' % (tacho * 5.5555555555))
			self.s_connects.bodies['nxt']['cons'][0]['con'].message_write(3,'2')
			self.s_locks['nxt'].release()
		else:
			pass

		# Set self.position to the new value
		self.position										= degrees

	# Get the state of the head motor
	def state(self):
		m_a													= Motor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_A)
		self.s_locks['nxt'].acquire()
		state												= m_a.get_output_state()
		self.s_locks['nxt'].release()
		print state

	# Reset drive states
	def reset(self):
		m_a													= Motor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_A)
		self.s_locks['nxt'].acquire()
		m_a.reset_position(False)
		self.s_locks['nxt'].release()
