#!/usr/bin/env python
# My threading template

import threading
import Queue
import time

class ThreadTemplate (threading.Thread):
	# Create our threading template. Any changes in this class
	# are reflected accross all threads.
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		# Load our threading init
		threading.Thread.__init__(self)

		# Incude our global communication
		self.s_connects										= s_connects
		self.s_queues										= s_queues
		self.s_conds										= s_conds
		self.s_locks										= s_locks
		self.s_sema											= s_sema

		# Debugging output
		self.debug											= 25

	# Parse information sent into the queue
	def parse_queue(self, block=True, timeout=0.25):
		try:
			# We "pop" an item off the start of the queue by calling
			# the get method. Once we have the item in a list, we grab
			# the function name and arguments to call. The arguments
			# are placed into the method using a variadic call by
			# prepending the ** to the beginning of the argument.
			runner										= self.s_queues.get(self.getName(), block=block, timeout=timeout)
			getattr(self,runner[1])(**runner[2])
		except Queue.Empty:
			# Nothing left to do, time to die
			return

	# Send a message to another thread queue
	def send(self, thread, function, args='', priority=0, block=True, timeout=None):
		self.s_queues.put(thread=thread, function=function, args=args, priority=priority, block=block, timeout=timeout)

	# Change our debugging level
	def set_debug(self, level=0):
		self.debug											= int(level)

	# Show our debugging level
	def show_debug(self):
		print self.debug

	# Output wrapper for displaying messages
	def display(self, message, level=0):
		# Make sure we want to display output at this debug level
		if self.debug >= int(level):
			self.s_queues.put('console','display_output',{'message':message})

	# Close the thread
	def close(self):
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)
		# Remove our queue
		self.s_queues.remove(self.getName())

		# Cant use the exit() call as this invokes string __exit__
		raise SystemExit
