import threading
import Queue
import time
import cPickle
import Tkinter
import ttk

import thread_template

class gui(thread_template.ThreadTemplate):
	""" Threaded object to send bluetooth messages to the ld3w controller. This
		lets us generate information about our true location within the world.
		We use this information to try keep track of positions that our relative
		data generator gathers. Once we create a map, we get the gps coordinates
		and name the map by the coordinates. When we read a map, we get the gps
		coordinates and try find a map of the location we are in.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		thread_template.ThreadTemplate.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('gui')
		self.root = Tkinter.Tk()

	def run(self):
		""" Our gps loop keeps polling the gps reciever to try get a new reading
			for our location. Once we have a reading, we tell the rest of the
			system.
		"""
		self.setName('gui')
		self.display('%s:\t\t\t\tStarting thread' % self.getName(), level=10)

		# Loop in the thread and wait for items in the queue and events from tk
		self.poll()
		self.root.mainloop()

		# All done. Close the thread
		self.display('%s:\t\t\t\tClosing thread' % self.getName(), level=10)

	def poll(self):
		""" Run the tkinter main loop polling gor updates from our queue
		"""
		self.parse_queue()
		self.root.after(0, self.poll)

	def parse_command(self, buff):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		# We have a command, proccess it
		if buff == '':
			return
		else:
			buff_v											= buff.split(' ')

		# Parse all gps functions
		if buff_v[0] == 'gui':
			# Check we have enough commands
			if not len(buff_v) >= 2:
				print "Not enough options"
				return

			# Start the tk interface
			if buff_v[1] == 'start':
				self.s_queues.put('gui','start',{})
			# Takeoff
			elif buff_v[1] == 'stop':
				self.s_queues.put('gui','stop',{})
			# Help system
			elif buff_v[1] == 'help':
				self.s_queues.put('gui','parse_help',{})
			# Check debug level
			elif buff_v[1] == 'debug':
				# if we dont have a value, just return the current level
				if len(buff_v) >= 3:
					self.s_queues.put('gui','set_debug',{'level':buff_v[2]})
				else:
					self.s_queues.put('gui','show_debug',{})
			else:
				print 'Command %s not found' % buff_v[1]

	def parse_help(self):
		""" Display help information for using the threads object. These need
			to be returned as a dictionary of options so we can display them
			inside other interfaces.
		"""
		print('\n## gui #####################################')
		print('gui info			\tList the connections')
		print('gui start			\t\t\tAdd a connection')
		print('gui stop			\t\tRemove a connection')
