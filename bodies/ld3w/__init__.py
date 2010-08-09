""" This library deifines how the system should communicate with the nmea based
	Nokia LD-3W gps device. The device works over bluetooth, so in order to use
	it, we first create a bluetooth connection. This is done within the our
	connection file. Once we have a connection to the device, we create a socket
	The imformation is then parsed by the nmea library.
"""
