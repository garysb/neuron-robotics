#!/usr/bin/env python
import sys
from qt import *
from qtgl import *
from OpenGL.GL import *
import CVtypes
from Image import *

class visualMap(QGLWidget):
	def __init__(self,parent=None,name=None):
		QGLWidget.__init__(self,parent,name)
		self.cap											= CVtypes.cv.CreateCameraCapture(0)
		self.setAutoBufferSwap(True)
		# Create an image for testing
		img													= open('test.jpg')
		self.img_width										= img.size[0]
		self.img_height										= img.size[1]
		self.image											= img.tostring("raw", "RGBX", 0, -1)

		self.startTimer(10)

	def timerEvent(self,event):
		self.updateGL()

	def paintGL(self):
		img													= CVtypes.cvRetrieveFrame(self.cap)
		print 'W: %s, H: %s, D: %s, C: %s' % (img[0].width, img[0].height, img[0].depth, img[0].nChannels)
		glClearColor(0.5, 0.5, 0.5, 0.0)
		img_bitmap											= CVtypes.cvImageAsBitmap(img)
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glRasterPos2i(0,0)
		glDrawPixels(img[0].width,img[0].height, GL_RGB, GL_UNSIGNED_BYTE, img[0].imageData)

	def resizeGL(self,width,height):
		pass

	def initializeGL(self):
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();
		glOrtho(-0.1, 1.0, -1.0, 5.0, 0.0, 10.0)

class MainWindow(QMainWindow):

	def __init__(self, *args):
		apply(QMainWindow.__init__, (self,) + args)
		self.image											= visualMap(self)
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
