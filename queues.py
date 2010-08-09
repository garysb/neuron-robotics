#!/usr/bin/python
# Control a thread queue. The purpose of this is to create
# a multi-queue. For each new thread created, a queue with
# built in priority is created. This queue is then passed
# into each thread. We then call get to fetch the queue for
# that thread.

import Queue, bisect

class PriorityQueue(Queue.Queue):
	def _put(self, item):
		self.queue.append(item)
		# FIXME: Need to fix priorities
		#bisect.insort(self.queue, item)

# Extend PriorityQueue to let us run multiple queues at once
class sysQueues:
	def __init__(self):
		# Create a blank dictionary
		self.queue_dict				= {}

	# Fetch a list of all our queues
	def queues(self):
		return self.queue_dict.keys()

	# Add a queue to the list
	def create(self, thread):
		self.queue_dict[thread]		= PriorityQueue(0)

	# Remove a queue from the list
	def remove(self, thread):
		del self.queue_dict[thread]

	# Put an item in a queue
	def put(self, thread, function, args='', priority=0, block=True, timeout=None):
		try:
			self.queue_dict[thread].put((priority, function, args), block, timeout)
		except:
			pass

	# Get a value from the queue
	def get(self, thread, block=True, timeout=None):
		return self.queue_dict[thread].get(block, timeout)

	# Get the size of a queue
	def qsize(self, thread):
		return self.queue_dict[thread].qsize()

	# return true if queue is empty
	# FIXME: Need to implement this
	def empty(self, thread):
		return self.queue_dict[thread].empty()

	# Flush data in a queue
	def flush(self,thread):
		return

	# Return true if queue is full
	def full(self, thread):
		return self.queue_dict[thread].full()

	# Fetch item from a queue without waiting
	def get_nowait(self, thread):
		return self.queue_dict[thread].get_nowait()

	# Put item on queue without waiting
	def put_nowait(self, thread, function, args='', priority=0):
		return self.queue_dict[thread].put_nowait((priority, function, args))
