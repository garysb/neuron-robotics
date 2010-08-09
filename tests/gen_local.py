#!/usr/bin/env python
from __future__ import division
from math import radians, cos, sin, pi, sqrt, ceil, floor
import sys
import socket
import cPickle
import bz2
import time
import random

# The hit angles we want to test
#angles														= [-90,90,0,-45,45]
#angles														= [0]
angles														= [-90,-75,-60,-45,-30,-15,0,15,30,45,60,75,90]

# Maximum sensor reading (in mm)
max_value													= 2550
values														= []

# Grid size (in cells)
columns														= 51
rows														= 51
# We dont allow even numbers, so if so, increase by one
if columns % 2 == 0: columns								+= 1
if rows % 2 == 0: rows										+= 1

# Cell sizes
cell														= {}
cell['mmx']													= (max_value * 2.0) / columns
cell['mmy']													= (max_value * 2.0) / rows

# Define our center point (this is where the sensors are)
center														= {}
# Center in mm
center['mmx']												= max_value
center['mmy']												= max_value
# Center in cells
center['cx']												= int(columns / 2.0)
center['cy']												= int(rows / 2.0)

grid														= [[0.5 for col in range(columns)] for row in range(rows)]

# Socket server setup
server_socket												= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port														= 54321
listen														= 5
timeout														= 1
values														= []
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("", port))
server_socket.listen(listen)
server_socket.settimeout(timeout)

def gen_values(angles=[0,-45,-90,45,90]):
	""" Simple function to randomly generate some values for our queue """
	global values
	global grid
	ranges													= random.sample(range(1,max_value), len(angles))
	values													= []
	for i in angles:
		reading												= {}
		reading['value']									= ranges.pop()
		reading['angle']									= i
		values.append(reading)
	grid													= [[0.5 for col in range(columns)] for row in range(rows)]
	sensorHits()

	# set the origin of sensor empty, this is where the robot is
	grid[center['cx']][center['cy']]						= 2.0
	return grid

def sensorHits():
	"""	Given the hits we recieve from our sensor (in this case, random points,
		calculate the location where we hit a point within our grid.
	"""
	global values
	for i in range(len(values)):
		# Check that the distance is less than the max range
		dist												= values[i]['value']
		if dist < max_value:
			values[i]['hit']								= True
		else:
			values[i]['hit']								= False

		# Set the hit cartesian position
		values[i]['rise']									= cos(radians(values[i]['angle'])) * dist
		values[i]['run']									= sin(radians(values[i]['angle'])) * dist
		values[i]['hit_run']								= int(values[i]['run']/cell['mmx'])
		values[i]['hit_rise']								= int(values[i]['rise']/cell['mmy'])

		# Calculate the steps we need to take
		# FIXME: Need a better way of using max on negative numbers
		if values[i]['hit_run'] < 0:
			num_a											= values[i]['hit_run'] * -1
		else:
			num_a											= values[i]['hit_run']
		if values[i]['hit_rise'] < 0:
			num_b											= values[i]['hit_rise'] * -1
		else:
			num_b											= values[i]['hit_rise']

		values[i]['steps']									= int(max(num_a, num_b))

		place_hits(values[i])

def place_hits(value):
	"""
	Initially only compute occupancies on the line from the robot to
	the sensor hit.
	"""
	#print 'Angle: %.0f' % value['angle']
	#print 'Distc: %.0f' % value['value']
	#print 'Steps: %s' % value['steps']
	#print 'Rise : %.0f' % value['rise']
	#print 'Run  : %.0f\n' % value['run']

	# If we have a hitpoint, add it to the grid
	if value['hit']:
		grid[center['cy']-value['hit_rise']][center['cx']+value['hit_run']]				= 1.0

	# Calculate the distance each run and rise step should consume
	if value['steps']:
		run_start												= center['mmy']
		rise_start												= center['mmx']
		run_step												= value['run']/value['steps']
		rise_step												= value['rise']/value['steps']

		#print 'RiseS: %.0f' % rise_step
		#print 'RunS : %.0f' % run_step

		# For each step, add our start and our run/rise step values
		for step in range(value['steps']-1):
			run_start											+= run_step
			rise_start											-= rise_step
			run_val												= int(run_start/cell['mmx'])
			rise_val											= int(rise_start/cell['mmy'])
			a													= rise_val
			b													= run_val
			#print 'RiseC: %.0f' % a
			#print 'RunC : %.0f' % b
			grid[rise_val][run_val]								= 0.0

# Catch keyboard interrupts
try:
	# Loop in the thread and wait for items in the queue
	while 1:
		# Build our data to be sent to the client
		data													= {}
		data['grid']											= gen_values(angles)
		data['values']											= values
		data['max_value']										= max_value
		data['rows']											= rows
		data['columns']											= columns

		#for i in grid:
		#	print '%s' % i

		try:
			client_socket, address							= server_socket.accept()
			client_socket.send(bz2.compress(cPickle.dumps(data)))
			client_socket.close()
		except socket.timeout:
			pass

except KeyboardInterrupt:
	print "Goodbye!"
