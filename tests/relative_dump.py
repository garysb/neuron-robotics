#!/usr/bin/env python
import socket
import cPickle
import time
import bz2

stop														= False

while not stop:
	client_socket											= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(("localhost", 54320))
	while 1:
		values												= cPickle.loads(bz2.decompress(client_socket.recv(8192)))
		client_socket.close()
		print len(values)
		break;
