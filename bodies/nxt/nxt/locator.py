# nxt.locator module -- Locate LEGO Minstorms NXT bricks via USB or Bluetooth

class BrickNotFoundError(Exception):
	pass

def find_bricks(host=None, name=None):
	#try:
	#	import usbsock
	#	socks						= usbsock.find_bricks(host, name)
	#	for s in socks:
	#		yield s
	#except ImportError:
	#	pass
	try:
		import bluesock
		from bluetooth import BluetoothError
		try:
			socks					= bluesock.find_bricks(host, name)
			for s in socks:
				yield s
		except BluetoothError:
			pass
	except ImportError:
		pass

def find_one_brick(host=None, name=None):
	for s in find_bricks(host, name):
		return s
	raise BrickNotFoundError
