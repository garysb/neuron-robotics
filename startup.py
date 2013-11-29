#!/usr/bin/env python
# vim: set ts=8 sw=8 sts=8 list nu:

# Main includes
import sys
import time
from threading import *

# Thread message queueing and priortising
import Queue
from queues import sysQueues
from connections import sysConnects
from threads import sysThreads

# Setup threads, connections, conditions, queues, locks, and semophores
s_conds = {}
s_locks = {}
s_sema = {}

s_queues = sysQueues()
s_connects = sysConnects(s_queues, s_conds, s_locks, s_sema)
s_threads = sysThreads(s_queues, s_connects, s_conds, s_locks, s_sema)

# Create our main control queue
s_queues.create('control')

# Close all threads and exit
def quit_sys():
	global threads

	# Close all our threads
	for i in s_threads.t_dict:
		s_queues.put(i,'close',{})

	# Force the console to close
	s_threads.t_dict['console']['thread'].close()

	raise SystemExit

# Parse information sent into the queue
def parse_queue(block=False, timeout=1):
	while True:
		try:
			# We "pop" an item off the start of the queue by calling
			# the get method. Once we have the item in a list, we grab
			# the function name and arguments to call. The arguments
			# are placed into the method using a variadic call by
			# prepending the ** to the beginning of the argument.
			runner = s_queues.get('control', block=False, timeout=1)
			globals()[runner[1]](**runner[2])
		except Queue.Empty:
			# Nothing left to do, time to die
			return

# Start our console system
s_locks['con'] = Lock()
s_threads.create('console')

s_queues.put('console','display',{'message':'control:\t\t\tStarting system'})
while 1:
	time.sleep(0.025)
	parse_queue()
	s_connects.parse_queue()
	s_threads.parse_queue()

