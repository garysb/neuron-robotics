#!/usr/bin/python

from threading import Lock
import os.path
import string
import Queue

# FIXME:Within the get_list method (a method to return a list of all active
#		connections, we need a way to fetch the sub connections. If we have
#		more than one instance of a specific body type, we create a list of
#		the bodies. We currently dont return these.

class sysConnects:
	""" This manages our connections to a body. In order to use this we need
		to define a module containing all methods to create the connection,
		maintain the connection and close it. Once a connection has been
		created, we place it in a connection pool to be accessed at a later
		time by our threads.
	"""

	def __init__(self, s_queues, s_conds, s_locks, s_sema):
		""" During initialisation we create a dictionary that holds all our
			connections. Due to the fact that we could have multiple bodies
			of the same type, each entry in the dictionary contains a list.
			Each entry in the list contains the body socket and connection.
		"""
		self.s_queues										= s_queues
		self.s_conds										= s_conds
		self.s_locks										= s_locks
		self.s_sema											= s_sema

		self.s_queues.create('connects')

		if os.path.isdir('bodies'):
			# The bodies directory exists, so now create our connections.
			self.bodies										= {}
		else:
			# We dont have the bodies directory. Report an error.
			# FIXME: We need a standardised way to report errors.
			pass

	def parse_queue(self, block=False, timeout=1):
		""" We run parse_queue in a loop to check if we have any commands to
			execute within this object. When we have a command within the queue
			we remove it from the queue and then pass it into getattr. This
			then executes it localy within our object. We also place the attrs
			in the getattr function by using variadic function initiators by
			placing the '**' before the option list.
		"""
		while True:
			try:
				runner										= self.s_queues.get('connects', block=block, timeout=timeout)
				getattr(self,runner[1])(**runner[2])
			except Queue.Empty:
				return

	def parse_command(self, buff):
		""" When we are running the system, we dont want to be stuck into using
			one interface type. By executing the commands locally and returning
			the result to the calling party, we can get around this. Just note
			that we get the whole command here, so we need to first strip off
			the 'connects' part. Also, all commands should be placed into the
			queue and not run directly. This is so that our prioritising works
			properly.
		"""
		if buff == '':
			return
		else:
			buff_v				= buff.split(' ')
		if buff_v[0] == 'connects':
			if not len(buff_v) >= 2:
				print "Not enough options"
				return
			if buff_v[1] == 'remove':
				self.s_queues.put('connects', 'remove',{'body':buff_v[2]})
			elif buff_v[1] == 'add':
				# Check if we entered a mac address, if so pass it on
				if not len(buff_v) >= 4:
					self.s_queues.put('connects','create',{'body':buff_v[2]})
				else:
					self.s_queues.put('connects','create',{'body':buff_v[2], 'unique':buff_v[3]})
			elif buff_v[1] == 'reload':
				self.s_queues.put('connects','recreate',{'body':buff_v[2]})
			elif buff_v[1] == 'list':
				print self.bodies.keys()
			elif buff_v[1] == 'help':
				self.s_queues.put('connects','parse_help',{})
			else:
				print 'You havnt invented the "%s" command yet!' % buff_v[1]

	def parse_help(self):
		""" Display help information for using the threads object. These need
			to be returned as a dictionary of options so we can display them
			inside other interfaces.
		"""
		print('\n## connections #####################################')
		print('connects list			\tList the connections')
		print('connects add [con]		\t\t\tAdd a connection')
		print('connects remove [con]	\t\tRemove a connection')

	def get_list(self):
		""" The get_list method returns a list of the bodies we are connected
			to. When we only have one connection to a body type, then we only
			return the name of the body type. If on the outher hand, we have
			a list of multiple bodies of the same type, then we return a list
			of the bodies of that type.
		"""
		print self.bodies.keys()

	def create(self, body='simulator', unique=None):
		""" This method creates a connection to the device named by the value
			entered in the 'body' variable which is defaulted to the simulator
			body. The method looks for a directory in the bodies directory for
			the body name entered and looks for a file called connection.py
			within the directory. Once it has found the file, we import the
			file and execute the connect function contained within, we should
			now have the return data from that connection eg. a socket and a
			connection. This then gets placed into the connectionsdictionary.
		"""

		# First we check if we already have a connection to the body.
		if body in self.bodies:
			# We already have the body type in our connections, we dont need
			# to worry about loading the module, all we do is create our main
			# connection. We are in a list, so just append.
			if unique:
				self.bodies[body]['cons'].append(self.bodies[body]['module']['connection'].create(unique))
			else:
				self.bodies[body]['cons'].append(self.bodies[body]['module']['connection'].create())
		else:
			# We dont have any data regarding this body type. We need to look
			# for the directory holding the body details and load all of the
			# connection data into the modules dictionary.
			if os.path.isdir("bodies/%s" % body):
				self.bodies[body]							= {}
				self.bodies[body]['cons']					= []
				self.bodies[body]['module']					= {}

				# We have the body details, lets load the connection module.
				# Load the module into a variable.
				module										= 'bodies.%s.connection' % body
				fromlist									= []
				if string.find(module, '.'):
					fromlist								= string.split(module, '.')[:-1]
				self.bodies[body]['module']['connection']	= __import__(module, globals(), locals(), fromlist)

				# Now that we have made our structure, lets try connect to
				# the device.
				if unique:
					con										= self.bodies[body]['module']['connection'].create(unique)
				else:
					con										= self.bodies[body]['module']['connection'].create()
				if len(con) > 1:
					# We got a response, add it to the dictionary
					self.bodies[body]['cons'].append(con)
					self.s_locks[body]						= Lock()
				else:
					# We have a problem, we need to remove the module
					del self.bodies[body]
			else:
				# We dont have the body type defined. Report an error.
				# FIXME: Need to implement an error reporting system.
				pass

	def remove(self, body='simulator', unique='00:00:00:00:00:00'):
		""" This method removes a connection from our list of connections. If
			we have a connection that has multiple bodies, we only remove the
			unique connection and leave the modules and information in the
			connections dictionary. If this is the only connection to this
			type of body, we close the connection, then we unload the module
			which is held within the connections dictionary.
		"""

		# Check to make sure we are acually connected to the device before we
		# try to disconnect from the device.
		if body in self.bodies:
			# We have at least got one of these body types, if we have more
			# than one, we need to check it against the unique id to make sure
			# its the one we want to disconnect from.
			if len(self.bodies[body]['cons']) > 1:
				# We have more than one, lets check the ids of the bodies
				for i in self.bodies[body]['cons']:
					if i['id'] == unique:
						# We found it, lets close the connection and then tidy
						# up all of the memory used by this device.
						i['sock'].close()
						self.bodies[body]['cons'].pop(i)
						break
			else:
				# We only have one of these bodies. We can remove all the data
				# and the modules used by it.
				self.bodies[body]['cons'][0]['sock'].close()
				del self.bodies[body]['cons'][0]
				del self.bodies[body]
		else:
			# We havnt got this body in our connections list. We dont need to
			# do anything. We should probably report this to the system though.
			pass
