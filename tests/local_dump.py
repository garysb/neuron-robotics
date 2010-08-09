#!/usr/bin/env python
import socket
import cPickle
import time

stop														= False

while not stop:
	client_socket											= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(("localhost", 54321))
	while 1:
		values												= cPickle.loads(client_socket.recv(4096))
		client_socket.close()
		print values
		break;
