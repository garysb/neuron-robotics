#!/usr/bin/env python
from __future__ import division
import socket
from threading import Thread
import time
from Tkinter import *
from math import ceil
import cPickle

stop														= 0

class relative(Thread):
	""" This class is run as a thread. It read all input from the server socket
		and draws it onto the canvas, provided by the tkinter library.
	"""
	def __init__(self, root, width=500, height=500):
		Thread.__init__(self)

		# Grid size (in cells)
		self.columns										= 50
		self.rows											= 50
		# Set the grid margin (in px)
		self.margin											= {}
		self.margin['x']									= 20
		self.margin['y']									= 20
		self.window											= {}
		# Grid width and height (in pixels)
		self.window['gx']									= width
		self.window['gy']									= height
		# Windows true width and height with margin (in pixels)
		self.window['tx']									= self.window['gx'] + (2*self.margin['x'])
		self.window['ty']									= self.window['gy'] + (2*self.margin['y'])
		# Cell sizes
		self.cell											= {}
		# The width and height of cells (in pixels)
		self.cell['pxx']									= self.window['gx'] / self.columns
		self.cell['pxy']									= self.window['gy'] / self.rows
		# Define our center point (this is where the sensors are)
		self.center											= {}
		# Center in cells
		self.center['cx']									= ceil(self.columns / 2.0 - 1)
		self.center['cy']									= ceil(self.rows / 2.0 - 1)

		self.cells											= [[0.5 for col in range(self.columns)]
																for row in range(self.rows)]
		self.step											= 0
		# Colors
		self.bgcolor										= '#EEEEEE'
		self.grid_color1									= '#DDFFDD'
		self.grid_color2									= '#DDDDFF'
		self.grid_color4									= '#FFDDDD'
		self.cell_color1									= '#00FF00'
		self.cell_color2									= '#EEEEEE'
		self.cell_color3									= '#FF0000'
		self.cell_color4									= '#000000'

		self.root											= root
		self.canvas											= Canvas(self.root, width=540, height=540, bg='#EEEEEE')
		self.canvas.pack(fill='both', expand=1)

	def run(self):
		""" This method proccesses our commands, then once all our commands hav
			run, consume an item from our queue. This will wait for a set time
			set in the queue.get method.
		"""
		self.setName('canvaser')
		# Setup the grid
		self.draw_cells()
		self.draw()
		self.reset_cells()

		while not stop:
			try:
				client_socket								= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client_socket.connect(("localhost", 54320))
				while 1:
					self.reset_cells()
					self.cells								= cPickle.loads(client_socket.recv(4096))
					client_socket.close()
					self.redraw_cells()
					break;
			except:
					self.reset_cells()
					self.cells[5][5]						= 2.0
					self.redraw_cells()

	def reset_cells(self, value = 0.5):
		# First copy the old grid so that we can use the backup to redraw old
		# used blocks, then we reset all the values to be blank
		self.old_cells										= self.cells
		self.cells											= [[value for col in range(self.columns)]
																for row in range(self.rows)]

	def color(self, value):
		""" Calculate the color of a specific block depending on which value
			was entered.
		"""
		if value == 0.0:
			return self.cell_color1
		elif value == 0.5:
			return self.cell_color2
		elif value == 1.0:
			return self.cell_color3
		else:
			return self.cell_color4

	def inRange(self, row, column):
		""" Check if a hit value is within range
		"""
		return row >= 0 and row < self.rows and column >= 0 and column < self.columns

	def draw(self):
		self.canvas.pack(fill='both', expand=1)
		pass

	def draw_cells(self):
		""" The way this system works is that we first create all our block and
			place them on the canvas. Once we have these blocks in position, we
			then get our values and change the color of the blocks we need.
		"""
		# For each row
		for a in range(self.rows):
			# For each column in the row
			for b in range(self.columns):
				i = self.columns - 1 - b
				j = a

				self.canvas.create_rectangle(
										int(self.margin['x'] + j * self.cell['pxx']),
										int(self.margin['y'] + i * self.cell['pxy']),
										int(self.margin['x'] + (j + 1) * self.cell['pxx']),
										int(self.margin['y'] + (i + 1) * self.cell['pxy']),
										width=0,
										fill=self.cell_color2,
										tag="cell_%s_%s" % (a, b))

	def redraw_cells(self, full=True):
		# We only want to blank out the old values and redraw the new ones
		for a in range(self.rows):
			for b in range(self.columns):
				i = self.columns - 1 - b
				j = a

				# Check if the old grid had a value here
				if self.old_cells[a][b] != 0.5 and self.cells[a][b] == 0.5:
					self.canvas.itemconfig("cell_%s_%s" % (a, b), fill=self.cell_color2)
				# Now if we need to, draw the new value in its block
				if self.cells[a][b] != 0.5:
					self.canvas.itemconfig("cell_%s_%s" % (a, b), fill=self.color(self.cells[a][b]))

def main():
	global stop
	root													= Tk()
	root.title('Relative Map')
	# Create our thread to update the canvas
	t_canvas												= relative(root)
	t_canvas.start()
	try:
		root.mainloop()
	finally:
		stop												= 1

main()
