from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import re
import cgi

class HTTPRequestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		""" Request an action from a specific item. This wont return the result
			of the object itself, it will only return the result of placing the
			call in the call queue.
		"""
		if None != re.search('/api/v1/addrecord/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
				recordID = self.path.split('/')[-1]
				LocalData.records[recordID] = data
				print "record %s is added successfully" % recordID
			else:
				data = {}

			self.send_response(200)
			self.end_headers()
		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		return

	def do_GET(self):
		""" Fetch any messages that need to be displayed on the system. Need to
			find a better way to handle this.
		"""
		queues = self.server.s_queues
		if None != re.search('/api/v1/', self.path):
			request = self.path.split('/')

			if request[3] in queues.queues():
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				data = queues.read(request[3])
				print data
				self.wfile.write(data)
			else:
				self.send_response(400, 'Bad Request: record does not exist')
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
		else:
			self.send_response(404)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	allow_reuse_address = True

	def __init__(self, server_address, RequestHandlerClass, s_queues):
		self.s_queues = s_queues
		HTTPServer.__init__(self, server_address, RequestHandlerClass)

	def shutdown(self):
		self.socket.close()
		HTTPServer.shutdown(self)

class SimpleHttpServer():
	def __init__(self, s_queues, ip, port):
		self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler, s_queues)

	def start(self):
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()

	def waitForThread(self):
		self.server_thread.join()

	def stop(self):
		self.server.shutdown()
		self.waitForThread()
