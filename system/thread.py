#!/usr/bin/env python
# vim: set ts=8 sw=8 sts=8 list nu:
# My threading template

import threading
import Queue

class Thread(threading.Thread):
	"""Create our threading template. Any changes in this class are reflected
		accross all threads.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		""" Initiate our object ensuring we call any init needed for the main
			threading object.
		"""
		threading.Thread.__init__(self)

		self.s_connects = s_connects
		self.s_queues = s_queues
		self.s_conds = s_conds
		self.s_locks = s_locks
		self.s_sema = s_sema

	def parse_queue(self, block=True, timeout=0.25):
		""" We "pop" an item off the start of the queue by calling get method.
			Once we have the item in a list, we grab the function name and
			arguments to call. The arguments are placed into the method using a
			variadic call by prepending the ** to the beginning of the argument.
		"""
		try:
			runner = self.s_queues.get(self.name, block=block, timeout=timeout)
			getattr(self, runner[1])(**runner[2])
		except Queue.Empty:
			# Nothing left to do, time to die
			return

	def parse_action(self, action):
		""" When we are running the system, we dont want to be stuck into using
			one interface type. By executing the commands locally and returning
			the result to the calling party, we can get around this. Just note
			that we get the whole command here, so we need to first strip off
			the 'threads' part. Also, all commands should be placed into the
			queue and not run dirrectly. This is so that our prioritising works
			properly.
		"""
		try:
			if len(action) == 1:
				action.append('read')

			call = getattr(self, action[1], None)

			if callable(call):
				values = dict([v.split(':') for v in action[2:]])
				self.s_queues.put(action[0], action[1], values)
			else:
				print "%s action not found in %s" % (action[1], action[0])
		except:
			print "error calling %s in %s" % (action[0], action[1])

	#def send(self, thread, function, args='', priority=0, block=True, timeout=None):
	#	""" Send a message to another thread queue
	#	"""
	#	self.s_queues.put(thread=thread, function=function, args=args, priority=priority, block=block, timeout=timeout)

	def output(self, message):
		""" When we are running the system, we dont want to be stuck into using
			one interface type. By executing the commands locally and returning
			the result to the calling party, we can get around this. Just note
			that we get the whole command here, so we need to first strip off
			the 'threads' part. Also, all commands should be placed into the
			queue and not run dirrectly. This is so that our prioritising works
			properly.
		"""
		self.s_queues.write(self.name, message)

	def close(self):
		""" Close the thread
		"""
		# Remove our queue
		self.s_queues.remove(self.name)

		# Cant use the exit() call as this invokes string __exit__
		raise SystemExit
