#!/usr/bin/env python
import bluetooth
import time

server_sock										= bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port											= bluetooth.get_available_port(bluetooth.RFCOMM)
uuid											= "1e0ca4ea-299d-4335-93eb-27fcfe7fa848"
server_sock.bind(("",port))
server_sock.listen(1)
print "listening on port %d" % port

try:
	if bluetooth.is_valid_uuid(uuid):
		bluetooth.advertise_service(server_sock,
									"nxt",
									bluetooth.to_full_uuid(uuid),
									service_classes=[bluetooth.SERIAL_PORT_CLASS,],
									profiles=[bluetooth.SERIAL_PORT_PROFILE,])
		client_sock,address						= server_sock.accept()
		print "Accepted connection from ",address
		while 1:
			cmd									= raw_input("Action?")
			# Send an action to the client
			client_sock.send(cmd)
			time.sleep(1)
			# Recieve a response from the client
			f									= open('out.jpg', 'w')
			f.write('')
			f.close()
			result								= ''
			data								= ''
			while not data == 'END':
				data							= client_sock.recv(1024)
				if data == 'END': break
				f								= open('out.jpg', 'ab')
				f.write(data)
				f.close()
				#result							= result.join(data)

			#while 1:
			#	data							= client_sock.recv(1024)
			#	print 'data: %s' % data
			#	if not data: break
			#	result							= result.join(data)

			#print 'now: %s' % data
			#result								= client_sock.recv(8192)
			#f									= open('out.jpg', 'w')
			#f.write(result)
			#f.close()
			#print "received [%s]" % result
			# Check what our result was from the client
			if result == 'exit':
				# The device has stopped, close the loop
				break

		client_sock.close()

	else:
		print 'Invalid uuid'
except KeyboardInterrupt:
	server_sock.close()
