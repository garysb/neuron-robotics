# nxt.usbsock module -- USB socket communication with LEGO Minstorms NXT

import usb
from nxt.brick import Brick

ID_VENDOR_LEGO = 0x0694
ID_PRODUCT_NXT = 0x0002

class USBSock(object):

	bsize = 60	# USB socket block size

	def __init__(self, device):
		self.device = device
		self.handle = None
		self.debug = False

	def __str__(self):
		return 'USB (%s)' % (self.device.filename)

	def connect(self):
		config = self.device.configurations[0]
		iface = config.interfaces[0][0]
		self.blk_out, self.blk_in = iface.endpoints
		self.handle = self.device.open()
		self.handle.setConfiguration(1)
		self.handle.claimInterface(0)
		self.handle.reset()
		return Brick(self)

	def close(self):
		self.device = None
		self.handle = None
		self.blk_out = None
		self.blk_in = None

	def send(self, data):
		if self.debug:
			print 'Send:',
			print ':'.join('%02x' % ord(c) for c in data)
		self.handle.bulkWrite(self.blk_out.address, data)

	def recv(self):
		data = self.handle.bulkRead(self.blk_in.address, 64)
		if self.debug:
			print 'Recv:',
			print ':'.join('%02x' % (c & 0xFF) for c in data)
		# NOTE: bulkRead returns a tuple of ints ... make it sane
		return ''.join(chr(d & 0xFF) for d in data)

def find_bricks(host=None, name=None):
	# FIXME: probably should check host and name
	for bus in usb.busses():
		for device in bus.devices:
			if device.idVendor == ID_VENDOR_LEGO and \
			   device.idProduct == ID_PRODUCT_NXT:
				yield USBSock(device)
