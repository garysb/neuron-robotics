#!/usr/bin/python
# Control a thread queue. The purpose of this is to create
# a multi-queue. For each new thread created, a queue with
# built in priority is created. This queue is then passed
# into each thread. We then call get to fetch the queue for
# that thread.

import Queue as Q
import bisect
import json

class PriorityQueue(Q.Queue):
	def _put(self, item):
		self.queue.append(item)
		# FIXME: Need to fix priorities
		#bisect.insort(self.queue, item)

# Extend PriorityQueue to let us run multiple queues at once
class Queue:
	def __init__(self):
		# Create a blank dictionary
		self.queues = {}

	# Fetch a list of all our queues
	def list(self):
		return self.queues.keys()

	# Add a queue to the list
	def create(self, thread):
		self.queues[thread] = {'action': PriorityQueue(0), 'message': PriorityQueue(0)}

	# Remove a queue from the list
	def remove(self, thread):
		del self.queues[thread]

	# Put an item in a queue
	def put(self, thread, function, args='', priority=0, block=True, timeout=None):
		try:
			self.queues[thread]['action'].put((priority, function, args), block, timeout)
		except:
			pass

	# Get a value from the queue
	def get(self, thread, block=True, timeout=None):
		return self.queues[thread]['action'].get(block, timeout)

	# Get the size of a queue
	def size(self, thread):
		return self.queues[thread]['action'].qsize()

	# return true if queue is empty
	# FIXME: Need to implement this
	def empty(self, thread):
		return self.queues[thread]['action'].empty()

	# Flush data in a queue
	def flush(self,thread):
		return

	# Return true if queue is full
	def full(self, thread):
		return self.queues[thread]['action'].full()

	# Fetch item from a queue without waiting
	def get_nowait(self, thread):
		return self.queues[thread]['action'].get_nowait()

	# Put item on queue without waiting
	def put_nowait(self, thread, function, args='', priority=0):
		return self.queues[thread]['action'].put_nowait((priority, function, args))

	def read(self, thread, block=True, timeout=None):
		""" Read the data within the message queue. This should be called within
			a thread that displays information and shouldnt be used as an action
			queue.
		"""
		try:
			return self.queues[thread]['message'].get_nowait()
		except Empty:
			return []

	def write(self, thread, data, priority=0, block=True, timeout=None):
		""" Write a message into our message queue. This will not be executed
			within our action list. The message is first compiled into a json
			string before getting inserted into the message queue.
		"""
		#try:
		if True:
			data = json.dumps(data)
			self.queues[thread]['message'].put(data, block, timeout)
		#except:
		#	print "error in write"
		#	pass
