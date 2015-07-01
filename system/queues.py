from system.thread import Thread

class queues(Thread):
	""" Threaded object to send bluetooth messages to the ld3w controller. This
		lets us generate information about our true location within the world.
		We use this information to try keep track of positions that our relative
		data generator gathers. Once we create a map, we get the gps coordinates
		and name the map by the coordinates. When we read a map, we get the gps
		coordinates and try find a map of the location we are in.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		Thread.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('queues')

	def run(self):
		""" Our gps loop keeps polling the gps reciever to try get a new reading
			for our location. Once we have a reading, we tell the rest of the
			system.
		"""
		self.name = 'queues'

		# Loop in the thread and wait for items in the queue
		while True:
			self.parse_queue()

	def create(self, id=None):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		self.s_queues.create(id)

	def read(self, id=None):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		queue_list = self.s_queues.list()
		for i in queue_list:
			print i

	def delete(self, id=None):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		self.s_queues.remove(id)

	def size(self, id=None):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		print self.s_queues.size(id)

	def flush(self, id=None):
		""" The parse_command method defines a list of actions that the drive
			object can perform. When we recieve a command in our buffer, we try
			to call the required method by placing it in the gps queue stack.
			This lets us keep our priority system running properly. Please note
			that actions that only return data arnt placed into the queue stack
			because they dont block the device.
		"""
		self.s_queues.flush(id)
