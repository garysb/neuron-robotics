#!/usr/bin/env python
# Control keyboard and display information
# FIXME: Need to migrate all display calls to use the queue

import threading
import time
import Queue
from system.thread import Thread
from interface.console import ttyLinux

class console(Thread):
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		Thread.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('console')

	# Default instant
	def run (self):
		self.setName('console')

		# Read our input from the console
		self.read_input()

	# Read input from the console
	def read_input(self):
		# Wait for input from the keyboard
		buff = ''
		buff_v = ['']

		# Loop until we recieve an "exit" string
		while buff != "exit":
			# FIXME: Need to fix buff_v
			buff_v = ['']

			# Make sure we catch EOF exception
			# FIXME: Need to remove the prompt when in a tty loop (eg.touch tail)
			try:
				buff = raw_input("]> ")
			except EOFError:
				time.sleep(1)
				print "got you"
				continue

			# We have a command, proccess it
			if buff == '':
				continue
			else:
				buff_v = buff.split(' ')

			## console ########################################################
			# Send a command to the queue
			#if buff_v[0] == 'send':
			#	# FIXME: Would love to find a good way of removing the eval
			#	self.send(**eval(buff[5:]))

			# Check for help
			if buff_v[0] == 'help':
				self.display_help()

			# Close all threads and exit program
			elif buff_v[0] == 'quit':
				buff = 'exit'
				self.s_queues.put('control','quit_sys',{})

			# Check our message queue
			elif buff_v[0] == 'messages':
				# Use the ttyLinux module to catch escape key
				try:
					ttyLinux.setSpecial()
					while 1:
						time.sleep(0.5)
						keys	= ttyLinux.readLookAhead()
						if [keys].__str__() == "[\'\\x1b\']":
							break
						self.parse_queue()
				finally:
					ttyLinux.setNormal()

			# Check if we need to send a command to a queue
			elif buff_v[0] in self.s_queues.list():
				self.s_queues.put(buff_v[0],'parse_action',{'action':buff_v})

			# We dont have this command
			else:
				print 'You havnt created %s yet!' % buff_v[0]

		# We have broken our loop, return to the calling method
		return

	# Print our output to the console
	def display_output(self, message):
		self.s_locks['con'].acquire()
		print message
		self.s_locks['con'].release()

	# Display help information on commands
	def display_help(self):
		# FIXME: Need to move the threads (eg.drive) help commands into the thread
		print('\nConsole commands:')
		print('## console ###########################################')
		print('help						You are looking at it you muppet!')
		print('send [msg]				\tSend a message to a queue to be processed')
		print('messages					Display all the console messages')
		print('quit						Close all threads and quit the program')
