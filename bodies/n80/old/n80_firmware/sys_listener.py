# Import our modules
import camera
import os
import socket

class image_push:
	def __init__(self, path):
		self._sockfd										= None
		self._path											= unicode(path + os.sep + 'img' + os.sep)

	def openSocket(self):
		''' Create a socket to accept our system to retrieve the images. '''
		try:
			self._sockfd									= socket.socket(socket.AF_BT, socket.SOCK_STREAM)
		except:
			raise

	def connect(self, addr, port):
		try:
			self._sockfd.connect((addr, port))
		except:
			raise

	def grabPhoto(self):
		try:
			img												= camera.take_photo(mode='RGB', size=(160, 120))
			img.save(self._path + '_foto_.jpg')
			return img
		except:
			raise

	def sendMessage(self, msg):
		try:
			self._sockfd.send(unicode(msg))
		except:
			raise

	def sendPhoto(self):
		try:
			BUFFER_READ										= 600
			foto											= open(self._path + '_foto_.jpg', 'rb')
			dimension										= os.stat(self._path + '_foto_.jpg').st_size
			while dimension >= 0:
				self._sockfd.send(foto.read(BUFFER_READ))
				dimension									-= BUFFER_READ
			self.sendMessage('__FOTO_END__')
			foto.close()
		except:
			raise

	def closeSocket(self):
		try:
			self._sockfd.close()
		except:
			raise
