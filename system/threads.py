# vim: ts=4 nowrap
import string
import Queue
import threading

class threads:
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
		self.name = 'threads'

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
				getattr(self, runner[1])(**runner[2])
			except Queue.Empty:
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

	def create(self, id='interface.console.console'):
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
			if string.find(id, '.'):
				fromlist = string.split(id, '.')
				t_name = fromlist.pop()

			self.t_dict[t_name] = {}
			self.t_dict[t_name]['module'] = __import__(id, globals(), locals(), fromlist, 0)

			# Create the thread and start it
			self.t_dict[t_name]['thread'] = getattr(self.t_dict[t_name]['module'], t_name) (
							self.s_queues,
							self.s_connects,
							self.s_conds,
							self.s_locks,
							self.s_sema)

			self.t_dict[t_name]['thread'].start()
		except KeyError:
			print 'KeyError %s: %s' % (id, id)

	def read(self, id=None):
		""" When we reload a thread, we need to first retrieve the module
			location from the already loaded module. We cant just reuse the
			current module because then any changes we have made wont be copied
			into the new instantiation of the thread. Once we have the name and
			location of the module, we stop the current running thread, then
			reload the module, then start the new instantiation.
		"""
		if id:
			print self.t_dict[id]
		else:
			for t in threading.enumerate():
				print t.name

	def update(self, id):
		""" When we reload a thread, we need to first retrieve the module
			location from the already loaded module. We cant just reuse the
			current module because then any changes we have made wont be copied
			into the new instantiation of the thread. Once we have the name and
			location of the module, we stop the current running thread, then
			reload the module, then start the new instantiation.
		"""
		try:
			module = self.t_dict[id]['module'].__name__
			reload(self.t_dict[id]['module'])
		except Exception as error:
			print "Error reloading: %s" % error

	def delete(self, id):
		""" When we remove a thread, we first tell the thread to close itself,
			then we wait for a while and remove the reference in the t_dict
			dictionary. Once we are sure its gone, we remove the module also.
		"""
		self.s_queues.put(id,'close',{})
		try:
			while self.t_dict[id]['thread'].isAlive():
				time.sleep(1)
		except:
			pass
		if self.t_dict.has_key(id):
			del self.t_dict[id]
