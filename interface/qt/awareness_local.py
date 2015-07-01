#!/usr/bin/env python
from qt import *
import sys
import socket
import time
from math import ceil
import random
import cPickle
import bz2

class localMap(QWidget):

	def __init__(self, *args):
		""" Initiate our mapping data and create the window """
		apply(QWidget.__init__,(self, ) + args)
		self.p_buffer										= QPixmap()
		self.setPalette(QPalette(QColor('#EEEEEE')))

		# Default values (Should be overwriten when socket connect)
		self.max_value										= 2550
		self.rows											= 25
		self.columns										= 25
		self.c_width										= 500 / self.columns
		self.c_height										= 500 / self.rows

		self.grid											= [[0.5 for col in range(self.columns)]
																	for row in range(self.rows)]

		# Run our data generation loop
		self.timer											= self.startTimer(1000)

	def timerEvent(self, ev):
		""" This method runs the main construct of our code. It starts first
			by trying to get our grid data from the server. Once we have the
			info, we build a pixmap within our buffer. Only when the pixmap
			has been built correctly, we replace the one being displayed.
		"""
		client_socket										= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client_socket.connect(("localhost", 54321))
			try:
				while 1:
					data									= cPickle.loads(bz2.decompress(client_socket.recv(1024)))
					client_socket.close()
					self.max_value							= data['max_value']
					self.rows								= data['rows']
					self.columns							= data['columns']
					self.values								= data['values']
					self.grid								= data['grid']
					break;
			except:
				pass
		except:
			pass

		self.p_display										= QPainter()
		self.p_display.begin(self.p_buffer)
		self.p_display.setPen(Qt.NoPen)
		#self.p_display.setPen(Qt.SolidLine)

		self.w_height										= self.p_buffer.size().height()
		self.w_width										= self.p_buffer.size().width()

		# Work out the cell size and create it
		cell												= QRect(0, 0, self.c_width, self.c_height)

		# For each row and column, draw a block
		for i in range(0, self.rows):
			for j in range(0, self.columns):
				self.p_display.setBrush(self.setColor(self.grid[i][j]))
				self.p_display.drawRect(cell)
				#cell.addCoords(c_width,0,c_height,0)
				cell.moveBy(self.c_width,0)
			cell.moveBy(-self.p_buffer.size().width(),self.c_height)

		# Clean out our buffer and display the pixmap
		self.p_display.flush()
		self.p_display.end()
		bitBlt(self, 0, 0, self.p_buffer)

	def paintEvent(self, ev):
		# blit the pixmap
		bitBlt(self, 0, 0, self.p_buffer)

	def setColor(self,value):
		""" We recieve a value in between 0.0 and 1.0 and return an appropriate
			color in between red and green.
		"""
		if value == 2.0:
			return QColor('#FFFFFF')

		return QColor(value*255,255-value*255,0)

	def resizeEvent(self, ev):
		# When the window gets resized, change the size of the buffer pixmap
		tmp													= QPixmap(self.p_buffer.size())
		bitBlt(tmp, 0, 0, self.p_buffer)

		# Set our new cell size
		b_size												= ev.size()
		self.c_width										= b_size.width() / self.columns
		self.c_height										= b_size.height() / self.rows

		b_size.setWidth(self.rows*self.c_width)
		b_size.setHeight(self.columns*self.c_height)
		# Set the new buffer size
		self.p_buffer.resize(b_size)
		self.p_buffer.fill()
		bitBlt(self.p_buffer, 0, 0, tmp)

class MainWindow(QMainWindow):

	def __init__(self, *args):
		apply(QMainWindow.__init__, (self,) + args)
		self.image											= localMap(self)
		self.setCentralWidget(self.image)
		self.setGeometry(100, 100, 500, 500)

def main(args):
	app														= QApplication(args)
	win														= MainWindow()
	win.show()
	app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
	app.exec_loop()

if __name__=="__main__":
	main(sys.argv)

