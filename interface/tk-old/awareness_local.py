#!/usr/bin/env python
from __future__ import division
import socket
from threading import Thread
import time
from Tkinter import *
from math import radians, cos, sin, pi, sqrt, ceil
import cPickle

stop														= 0

class local(Thread):
	""" This class is run as a thread. It read all input from the server socket
		and draws it onto the canvas, provided by the tkinter library.
	"""
	def __init__(self, root, width=250, height=250):
		Thread.__init__(self)

		# Maximum sensor reading (in mm)
		self.max_value										= 2550
		self.values											= []
		# Grid size (in cells)
		self.columns										= 25
		self.rows											= 25
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
		self.cell['mmx']									= (self.max_value * 2.0) / self.columns
		self.cell['mmy']									= (self.max_value * 2.0) / self.rows
		# Define our center point (this is where the sensors are)
		self.center											= {}
		# Center in mm
		self.center['mmx']									= self.max_value
		self.center['mmy']									= self.max_value
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
		self.canvas											= Canvas(self.root, width=290, height=290, bg='#EEEEEE')
		self.canvas.pack(fill='both', expand=1)

	def run(self):
		""" This method proccesses our commands, then once all our commands hav
			run, consume an item from our queue. This will wait for a set time
			set in the queue.get method.
		"""
		self.setName('canvaser')
		# Setup the grid
		self.draw_grid()
		self.draw_cells()
		self.draw()
		self.reset_cells()

		while not stop:
			client_socket									= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect(("localhost", 54321))
			while 1:
				self.reset_cells()
				self.cells									= cPickle.loads(client_socket.recv(4096))
				client_socket.close()
				self.redraw_cells()
				self.redraw_grid()
				break;

	def reset_cells(self, value = 0.5):
		# First copy the old grid so that we can use the backup to redraw old
		# used blocks, then we reset all the values to be blank
		self.old_cells										= self.cells
		self.cells											= [[value for col in range(self.columns)]
																for row in range(self.rows)]
		self.label											= [['' for col in range(self.columns)]
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

	def draw_grid(self):
		# Small lines
		for x in range(int(self.cell['pxx']+self.margin['x']), int(self.window['gx']+self.margin['x']), int(self.cell['pxx'])):
			self.canvas.create_line(x,
									self.margin['y'],
									x,
									self.window['gy']+self.margin['y'],
									fill=self.grid_color1,
									width=1,
									tag='grid_small')
		for y in range(int(self.cell['pxy']+self.margin['y']), int(self.window['gy']+self.margin['y']), int(self.cell['pxy'])):
			self.canvas.create_line(self.margin['x'],
									y,
									self.window['gx']+self.margin['x'],
									y,
									fill=self.grid_color1,
									width=1,
									tag='grid_small')

		# Medium lines
		for x in range(int(self.cell['pxx']*2+self.margin['x']), int(self.window['gx']+self.margin['x']), int(self.cell['pxx']*2)):
			self.canvas.create_line(x,
									self.margin['y'],
									x,
									self.window['gy']+self.margin['y'],
									fill=self.grid_color2,
									width=1,
									tag='grid_medium')
		for y in range(int(self.cell['pxy']*2+self.margin['y']), int(self.window['gy']+self.margin['y']), int(self.cell['pxy']*2)):
			self.canvas.create_line(self.margin['x'],
									y,
									self.window['gx']+self.margin['x'],
									y,
									fill=self.grid_color2,
									width=1,
									tag='grid_medium')

		# Large lines
		for x in range(int(self.cell['pxx']*4+self.margin['x']), int(self.window['gx']+self.margin['x']), int(self.cell['pxx']*4)):
			self.canvas.create_line(x,
									self.margin['y'],
									x,
									self.window['gy']+self.margin['y'],
									fill=self.grid_color4,
									width=1,
									tag='grid_large')
		for y in range(int(self.cell['pxy']*4+self.margin['y']), int(self.window['gy']+self.margin['y']), int(self.cell['pxy']*4)):
			self.canvas.create_line(self.margin['x'],
									y,
									self.window['gx']+self.margin['x'],
									y,
									fill=self.grid_color4,
									width=1,
									tag='grid_large')

		# Draw the border around the grid
		self.canvas.create_rectangle(self.margin['x'],
									self.margin['y'],
									self.window['gx']+self.margin['x'],
									self.window['gy']+self.margin['y'],
									outline='grey',
									tag='grid_border')

		# Show our scale
		scale												= ((self.max_value/self.columns) * 10) - 1
		self.canvas.create_line(self.margin['x']+(2*self.cell['pxx']),
								self.margin['y']+self.rows*self.cell['pxy']-self.cell['pxy']-(self.cell['pxy']/2),
								self.margin['x']+(self.cell['pxx']*6),
								self.margin['y']+self.rows*self.cell['pxy']-self.cell['pxy']-(self.cell['pxy']/2),
								arrow='both',
								width=1,
								fill='grey',
								tag='grid_scale')

		self.canvas.create_text(self.margin['x']+(4*self.cell['pxx']),
								self.margin['y']+self.rows*self.cell['pxy']-self.cell['pxy'] + 3 -(self.cell['pxy']/2),
								text='%smm' % scale,
								anchor='n',
								fill='grey',
								tag='grid_scale')

	def redraw_grid(self):
		self.canvas.lift('grid_small')
		self.canvas.lift('grid_medium')
		self.canvas.lift('grid_large')
		self.canvas.lift('grid_border')
		self.canvas.lift('grid_scale')

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
	root.title('Local Map')

	icon_image												= PhotoImage(file='icon.gif')
	icon													= Toplevel()
	Label(icon, image=icon_image).pack()
	root.iconwindow(icon)

	# Create our thread to update the canvas
	t_canvas												= local(root)
	t_canvas.start()
	try:
		root.mainloop()
	finally:
		stop												= 1

main()
