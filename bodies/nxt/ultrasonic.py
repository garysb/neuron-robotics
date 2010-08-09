#!/usr/bin/env python
# ultrasonic sensor thread

import threading
import time
from math import radians
from interfaces.console import ttyLinux
import thread_template
from bodies.nxt.nxt.sensor import *
import cPickle

class ultrasonic(thread_template.ThreadTemplate):
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('ultrasonic')
		# The maximum range (in millimeters)
		self.max_range										= 2550
		self.scan_lock										= False
		self.scan_tell										= []
		self.scan_results									= {}
		self.scan_results['max_range']						= self.max_range
		self.scan_results['values']							= []

	# Default instant
	def run(self):
		self.setName('ultrasonic')
		self.display('%s:\t\t\tStarting thread' % self.getName(), level=10)

		self.sensor_state									= 0
		self.passive										= True

		# Check the ultrasonic sensor is working properly
		self.display('%s:\t\t\tChecking sensor state' % self.getName(), level=25)
		try:
			self.s_locks['nxt'].acquire()
			self.display('%s:\t\t\t%scm' % (
				self.getName(),
				self.get_state()),
				level=25)
			self.s_locks['nxt'].release()
		except:
			self.display('%s:\t\t\tUnable to get sensor state. Closing thread.' % self.getName(), level=10)
			self.close()

		# Check our ultrasonic sensor state
		while True:
			self.parse_queue()
			#self._poll() # Dont need a continuous value unless asked for one

		# All done. Close the thread
		self.display('%s:\t\t\tClosing thread' % self.getName(), level=10)

	# Loop our function to check for a state change
	def _poll(self):
		time.sleep(0.25)
		try:
			self.s_locks['nxt'].acquire()
			self.sensor_state								= self.get_state()
			self.s_locks['nxt'].release()
			self.display('%s:\t\t\t%scm' % (self.getName(),self.sensor_state), level=50)
		except:
			self.display('%s:\t\t\tUnable to get sensor state' % self.getName(), level=25)

	# Parse our input commands
	def parse_command(self, buff):
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v				= buff.split(' ')

		# Parse all ultra sensor functions
		if buff_v[0] == 'ultrasonic':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Get the ultrasonic sensor state
			if buff_v[1] == 'state':
				self.s_queues.put('ultrasonic','state',{})
			# Set the ultrasound to transmit
			elif buff_v[1] == 'on':
				self.s_queues.put('ultrasonic','set_on',{})
			# Disable ultrasound transmission
			elif buff_v[1] == 'off':
				self.s_queues.put('ultrasonic','set_off',{})
			# Calibrate the ultrasound
			elif buff_v[1] == 'calibrate':
				# Check we have enough options (scale, divisor, zero)
				if len(buff_v) >= 5:
					self.s_queues.put('ultrasonic','calibrate',{'scale':buff_v[2],'divisor':buff_v[3],'zero':buff_v[4]})
				else:
					print 'Not enough options'
			elif buff_v[1] == 'calibration':
				self.s_queues.put('ultrasonic','get_calibration',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('ultrasonic','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('ultrasonic','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	# Check the state of the Ultrasonic sensor
	def get_state(self):
		# Check if we ping with ultrasound, or just read the result
		if self.passive:
			return UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).get_single_shot_measurement()
		else:
			return UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).get_passive()

	# Get the current ultrasonic sensor state
	def state(self):
		print self.sensor_state

	# Get the current ultrasonic sensor state
	def set_on(self):
		self.passive										= True
		return UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).get_single_shot_measurement()

	# Get the current ultrasonic sensor state
	def set_off(self):
		self.passive										= False
		return UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).get_passive()

	# Get the current calibration values
	def get_calibration(self):
		print libs.ultrasonic.get_calibration(self.s_connects.bodies['nxt']['cons'][0]['con'])

	# Calibrate the ultrasound sensor
	def calibrate(self, scale=0, divisor=0, zero=0):
		UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).set_actual_zero(int(zero))
		UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).set_actual_scale_factor(int(scale))
		UltrasonicSensor(self.s_connects.bodies['nxt']['cons'][0]['con'], PORT_1).set_actual_scale_divisor(int(divisor))

	def scan(self, tell='local', call='get_values', points=[0,-15,-30,-45,-60,-75,-90,15,30,45,60,75,90]):
		""" Given a callback thread and method, fetch the ultrasound scanning
			values and return it to the thread.
		"""
		# Check if we are already running a scan. If we are, dont try run it
		# again, instead, tell the system to return the same results to the
		# other thread also.
		if self.scan_lock:
			local_tell											= {'tell':tell,'call':call}
			self.scan_tell.append(local_tell)
		else:
			self.scan_lock										= True
			local_tell											= {'tell':tell,'call':call}
			self.scan_tell.append(local_tell)
			# Check if we have a list or pickled string
			if type(points) is list:
				points											= points
			else:
				points											= cPickle.loads(points)
			self.parse_queue(block=False, timeout=None)

			# Always set the head to the zero position to start
			self.s_queues.put('head','center',{})
			time.sleep(1)
			for i in points:
				self.parse_queue(block=False, timeout=None)
				tmp												= {}
				tmp['angle']									= radians(i)
				if i < 0:
					self.s_queues.put('head','left',{'degrees':(i*-1)})
					time.sleep(2)
					tmp['value']								= (int(self.get_state())*10)
					time.sleep(0.5)
				elif i > 0:
					self.s_queues.put('head','right',{'degrees':i})
					time.sleep(2)
					tmp['value']								= (int(self.get_state())*10)
					time.sleep(0.5)
				else:
					self.s_queues.put('head','center',{})
					time.sleep(2)
					tmp['value']								= (int(self.get_state())*10)
					time.sleep(0.5)

					# Check if we got a hit or not
					if tmp['value'] == self.max_range:
						tmp['hit']								= False
					else:
						tmp['hit']								= True

				# Now add the result to the list
				self.scan_results['values'].append(tmp)
				self.parse_queue(block=False, timeout=None)

			# We have the reading values, now return them to the callers
			while len(self.scan_tell) >= 1:
				teller											= self.scan_tell.pop()
				self.s_queues.put(teller['tell'],teller['call'],{'values':cPickle.dumps(self.scan_results)})

			# Reset our values and unlock our scanner
			self.scan_results['values']							= []
			self.scan_lock										= False
