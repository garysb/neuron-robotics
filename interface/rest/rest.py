import interface.rest.server
from system.thread import Thread

class rest(Thread):
	""" Threaded object to send bluetooth messages to the ld3w controller. This
		lets us generate information about our true location within the world.
		We use this information to try keep track of positions that our relative
		data generator gathers. Once we create a map, we get the gps coordinates
		and name the map by the coordinates. When we read a map, we get the gps
		coordinates and try find a map of the location we are in.
	"""
	def __init__(self, s_queues, s_connects, s_conds, s_locks, s_sema):
		Thread.__init__(self, s_queues, s_connects, s_conds, s_locks, s_sema)
		self.s_queues.create('rest')

	def run(self):
		""" Our gps loop keeps polling the gps reciever to try get a new reading
			for our location. Once we have a reading, we tell the rest of the
			system.
		"""
		self.name = 'rest'

		# Loop in the thread and wait for items in the queue and events from tk
		while True:
			self.parse_queue()

	def starter(self, ip='localhost', port=54321):
		self.s_queues.put(self.name,'start_server',{'ip':ip, 'port':port})

	def stoper(self):
		self.s_queues.put(self.name,'stop_server',{})

	def start_server(self, ip, port):
		self.server = interface.rest.server.SimpleHttpServer(self.s_queues, ip, int(port))
		print 'HTTP Server Running...........'
		self.server.start()

	def stop_server(self):
		self.server.stop()
