# vim: ts=4 nowrap
import string
import Queue
from threading import *

# FIXME:We need to be able to handle multiple threads of the same type. Eg.
#		if we have to nxt bodies, then we could have two ultrasound threads.
#		These would use different connections and different ports, but still
#		have the same module loaded. We would of course still be able to set
#		the local variables seperatly.

# FIXME:We need to validate that the thread have started/stopped correctly.
#		Due to the way we reload the modules (to allow us to modify live
#		code), we need to be able to validate the code and then return true
#		if the thread started properly.

# FIXME:We need a way to return the __doc__ to the caller. This is so that
#		can issue a command to the nature of 'threads start help' to give
#		us information on how to start threads.

class sysThreads:
	""" This object manages our threads. The system works by holding a local
		dictionary called self.t_dict. When we want to create a new thread, we
		start by finding the module containing the thread data. Once we find it
		we load the module into the dictionary (not the global module list)
		under 'module' and then instantiate the threads object and place it in
		'thread'. This gives us an easy path back to the module at any time.
	"""

	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		""" During initilisation we import our queues, connections, conditions.
			locks, and semaphors. This is so we can pass them into our threads.
			We also create a threads queue to handle communication with the
			outside world and our dictionary to hold the modules and threads.
		"""
		self.s_queues = s_queues
		self.s_connects = s_connects
		self.s_conds = s_conds
		self.s_locks = s_locks
		self.s_sema = s_sema
		self.s_queues.create('threads')

		self.t_dict = {}

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
				runner = self.s_queues.get('threads', block=block, timeout=timeout)
				getattr(self,runner[1])(**runner[2])
			except Queue.Empty:
				return

	def parse_command(self, buff):
		""" When we are running the system, we dont want to be stuck into using
			one interface type. By executing the commands locally and returning
			the result to the calling party, we can get around this. Just note
			that we get the whole command here, so we need to first strip off
			the 'threads' part. Also, all commands should be placed into the
			queue and not run dirrectly. This is so that our prioritising works
			properly.
		"""
		if buff == '':
			return
		else:
			buff_v = buff.split(' ')
		if buff_v[0] == 'threads':
			if not len(buff_v) >= 2:
				print "Not enough options"
				return
			if buff_v[1] == 'remove':
				self.s_queues.put('threads', 'remove',{'name':buff_v[2]})
			elif buff_v[1] == 'add':
				if len(buff_v) == 3:
					self.s_queues.put('threads','create',{'module':buff_v[2]})
				elif not len(buff_v) == 4:
					print "Not enough options", len(buff_v)
					return
				else:
					self.s_queues.put('threads','create',{'name':buff_v[2], 'module':buff_v[3]})
			elif buff_v[1] == 'reload':
				self.s_queues.put('threads','recreate',{'name':buff_v[2]})
			elif buff_v[1] == 'list':
				print ""
				for i in enumerate():
					print i
			elif buff_v[1] == 'help':
				self.s_queues.put('threads','parse_help',{})
			else:
				print 'You havnt invented the "%s" command yet!' % buff_v[1]

	def parse_help(self):
		""" Display help information for using the threads object. These need
			to be returned as a dictionary of options so we can display them
			inside other interfaces.
		"""
		print('\n## threads #########################################')
		print('threads list				\tList all threads currently running')
		print('threads add [thr]		\t\tStart a thread')
		print('threads remove [thr]		\t\tClose a thread')
		print('threads restart [thr]	\t\t\tRestart a thread')

	def create(self, name=False, module='interfaces.console.console'):
		""" due to the nature of our file system layout, we need to be able to
			specify the location that the threads module is located. to do this
			we pass in the module layout relative to the root directory of the
			startup.py script. When we find the module, we import it into our
			local t_dict dictionary under the name of the thread, so an example
			for the console would be, self.t_dict['console']['module']. We then
			initialise and start our thread under self.dict['console']['thread']
		"""
		try:
			# Load the module into a variable.
			fromlist = []
			if string.find(module, '.'):
				fromlist = string.split(module, '.')
				t_name = fromlist.pop()
			if name:
				t_name = name

			self.t_dict[t_name] = {}
			self.t_dict[t_name]['module'] = __import__(module, globals(), locals(), fromlist)

			# Create the thread and start it
			self.t_dict[t_name]['thread'] = getattr(self.t_dict[t_name]['module'], t_name)(
							self.s_queues,
							self.s_connects,
							self.s_conds,
							self.s_locks,
							self.s_sema)

			self.t_dict[t_name]['thread'].start()
		except KeyError:
			pass
		except ImportError:
			print 'Module not found'

	def remove(self, name):
		""" When we remove a thread, we first tell the thread to close itself,
			then we wait for a while and remove the reference in the t_dict
			dictionary. Once we are sure its gone, we remove the module also.
		"""
		self.s_queues.put(name,'close',{})
		try:
			while self.t_dict[name]['thread'].isAlive():
				time.sleep(1)
		except:
			pass
		if self.t_dict.has_key(name):
			del self.t_dict[name]

	def recreate(self, name):
		""" When we reload a thread, we need to first retrieve the module
			location from the already loaded module. We cant just reuse the
			current module because then any changes we have made wont be copied
			into the new instantiation of the thread. Once we have the name and
			location of the module, we stop the current running thread, then
			reload the module, then start the new instantiation.
		"""
		module = self.t_dict[name]['module'].__name__
		self.remove(name)
		self.create(name, module)

