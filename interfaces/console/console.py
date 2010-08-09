#!/usr/bin/env python
# Control keyboard and display information
# FIXME: Need to migrate all display calls to use the queue

import threading
import time
import Queue
import thread_template
from interfaces.console import ttyLinux

class console(thread_template.ThreadTemplate):
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('console')

	# Default instant
	def run (self):
		self.setName('console')
		self.display('%s:\t\t\tStarting thread' % self.getName(),level=10)

		# Read our input from the console
		self.read_input()

		# All done. Close the thread
		self.display('%s:\t\t\tClosing thread' % self.getName(),level=10)

	# Read input from the console
	def read_input(self):
		# Wait for input from the keyboard
		buff						= ''
		buff_v						= ['']

		# Loop until we recieve an "exit" string
		while buff != "exit":
			# FIXME: Need to fix buff_v
			buff_v					= ['']

			# Make sure we catch EOF exception
			# FIXME: Need to remove the prompt when in a tty loop (eg.touch tail)
			try:
				buff				= raw_input("NXT> ")
			except EOFError:
				time.sleep(1)
				continue

			# We have a command, proccess it
			if buff == '':
				continue
			else:
				buff_v				= buff.split(' ')

			## console ########################################################
			# Send a command to the queue
			if buff_v[0] == 'send':
				# FIXME: Would love to find a good way of removing the eval
				self.send(**eval(buff[5:]))

			# Check for help
			elif buff_v[0] == 'help':
				self.display_help()

			# Close all threads and exit program
			elif buff_v[0] == 'quit':
				buff				= 'exit'
				self.s_queues.put('control','quit_sys',{})

			# Return the battery level
			elif buff_v[0] == 'battery':
				print "%sMV" % self.s_connects['nxt']['con'].get_battery_level()

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

			## queues #########################################################
			elif buff_v[0] == 'queues':
				# Check we have enough commands
				if not len(buff_v) >= 2:
					print "Not enough options"
					continue

				# List our queues
				if buff_v[1] == 'list':
					queue_list		= self.s_queues.queues()
					for i in queue_list:
						print i

				# Check a queues size
				elif buff_v[1] == 'qsize':
					# Make sure we have a queue to view
					if len(buff_v) == 3:
						print self.s_queues.qsize(buff_v[2])
					else:
						print "We need a queue name to see its size"

				# Add a queue
				elif buff_v[1] == 'add':
					if len(buff_v) == 3:
						self.s_queues.create(buff_v[2])
					else:
						print "We need a queue name to add a queue"

				# Remove a queue
				elif buff_v[1] == 'remove':
					if len(buff_v) == 3:
						self.s_queues.remove(buff_v[2])
					else:
						print "We need a queue name to remove a queue"

				# Flush a queues commands
				elif buff_v[1] == 'flush':
					if len(buff_v) == 3:
						self.s_queues.flush(buff_v[2])
					else:
						print "We need a queue name to flush a queue"

				# We dont have this queues command
				else:
					print 'You havnt invented the "%s" command yet!' % buff_v[1]

			## connections ####################################################
			elif buff_v[0] == 'connections':
				# Check we have enough commands
				if not len(buff_v) >= 2:
					print "Not enough options"
					continue

				# List our active connections
				if buff_v[1] == 'list':
					for i in self.s_connects.keys():
						print i

				# Add a connection
				elif buff_v[1] == 'add':
					# We can only add two types of connections at the moment
					if buff_v[2] == 'nxt':
						self.s_queues.put('control', 'connect',{'con':buff_v[2]})
					elif buff_v[2] == 'gps':
						self.s_queues.put('control', 'connect',{'con':buff_v[2]})
					else:
						print 'We dont have a %s to connect to!' % buff_v[2]

				# Remove a connection
				elif buff_v[1] == 'remove':
					self.s_queues.put('control', 'disconnect',{'con':buff_v[2]})

				# We dont have this connections command
				else:
					print 'You havnt invented the "%s" command yet!' % buff_v[1]

			## misc #######################################################
			# FIXME: To be removed
			# GPS functions
			elif buff_v[0] == 'gps':
				# Check we have enough commands
				if not len(buff_v) >= 2:
					print "Not enough options"
					continue

				# Forward
				if buff_v[1] == 'show':
					if buff_v[2] == 'waypoints':
						self.s_queues.put('gps','list_waypoints',{})
				# Add waypoint
				if buff_v[1] == 'add':
					if buff_v[2] == 'waypoint':
						self.s_queues.put('gps','add_waypoint',{'longitude':buff_v[3],'latitude':buff_v[4]})

			# Check if we need to send a command to a queue
			elif buff_v[0] in self.s_queues.queues():
				self.s_queues.put(buff_v[0],'parse_command',{'buff':buff})

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
		print('help						You are looking at it muppet!')
		print('send [msg]				\tSend a message to a queue to be processed')
		print('messages					Display all the console messages')
		print('battery					Show the battery level')
		print('quit						Close all threads and quit the program')
		print('\n## threads #########################################')
		print('threads list				\tList all threads currently running')
		print('threads add [thr]		\t\tStart a thread')
		print('threads remove [thr]		\t\tClose a thread')
		print('threads restart [thr]	\t\t\tRestart a thread')
		print('\n## queues ##########################################')
		print('queues list				\tList the current queues')
		print('queues qsize [q]			\tShow the size of a queue')
		print('queues flush [q]			\tFlush data in a queue')
		print('queues add [q]			\t\tAdd a queue to the system')
		print('queues remove [q]		\t\tRemove a queue')
		print('\n## connections #####################################')
		print('connections list			\tList the connections')
		print('connections add [con]	\t\t\tAdd a connection (can be nxt or gps)')
		print('connections remove [con]	\t\tRemove a connection')
		print('\n## drive ###########################################')
		print('drive fd {mm}			\t\tDrive forward x millimeters')
		print('drive bk {mm}			\t\tDrive backwards x millimeters')
		print('drive sl {deg}			\t\tSpin left x degrees')
		print('drive sr {deg}			\t\tSpin right x degrees')
		print('drive state				\tReturn the state of the motors')
		print('drive reset				\tReset the drives state')
		print('drive debug {lvl}		\t\tSet/show the debug level')
		print('\n## touch ###########################################')
		print('touch state				\tReturn the state of the touch sensor')
		print('touch tail				\tContinuously print touch sensor state')
		print('touch debug {lvl}		\t\tSet/show the debug level')
		print('\n## light ###########################################')
		print('light [on|off]			\tTurn the light on or off')
		print('light state				\tReturn the state of the light sensor')
		print('light tail				\tContinuously print light sensor state')
		print('light debug {lvl}		\t\tSet/show the debug level')
		print('\n## sound ###########################################')
		print('sound state				\tReturn the state of the sound sensor')
		print('sound tail				\tContinuously print sound sensor state')
		print('sound debug {lvl}		\t\tSet/show the debug level')
		print('\n## ultrasound ######################################')
		print('ultrasound [on|off]		\tTurn the transmitter on or off')
		print('ultrasound calibrate		\tSet Scale, divisor, zero')
		print('ultrasound calibration	\tReturn the current calibration')
		print('ultrasound state			\tReturn the state of the ultrasound sensor')
		print('ultrasound tail			\t\tContinuously print ultrasound sensor state')
		print('ultrasound debug {lvl}	\t\t\tSet/show the debug level')

		print('gps show waypoints		\t\tShow the list of waypoints')
		print('gps add waypoint			\tAdd a waypoint to the queue')
