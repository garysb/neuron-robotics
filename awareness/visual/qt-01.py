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
		# Print our image dimensions
		#print 'W: %s, H: %s' % (self.img_width, self.img_height)
		# Copy the image into a gl texture
		#glEnable(GL_TEXTURE_2D)
		#self.texture										= 100#glGenTextures(1)
		#glBindTexture(GL_TEXTURE_2D, self.texture)
		#glPixelStorei(GL_UNPACK_ALIGNMENT,1)
		#glTexImage2D(GL_TEXTURE_2D, 0, 3, self.img_width, self.img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image)
		#glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.img_width,self.img_height,0,GL_RGBA,GL_UNSIGNED_BYTE,self.image)
		self.startTimer(10)

	def timerEvent(self,event):
		# Check if auto buffer swap is on
		#if self.autoBufferSwap:
			#print 'AutoBufferSwap is on'
		#else:
			#print 'AutoBufferSwap is off'
		## Check if double buffer is on
		#if self.doubleBuffer:
			#print 'doubleBuffer is on'
		#else:
			#print 'doubleBuffer is off'
		self.updateGL()

	def paintGL(self):
		img_rgb													= CVtypes.cvRetrieveFrame(self.cap)
		# convert bgr to rgb
		CVtypes.cvCvtColor(img_rgb, img_rgb, CVtypes.CV_BGR2RGB)
		CVtypes.cvFlip(img_rgb, None, 1)
		glClearColor(0.5, 0.5, 0.5, 0.0)
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		#glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
		glRasterPos2i(0,0)
		#glDrawPixels(self.img_width,self.img_height, GL_RGBA, GL_UNSIGNED_BYTE, self.image)
		glDrawPixels(img_rgb[0].width,img_rgb[0].height, GL_RGB, GL_UNSIGNED_BYTE, img_rgb[0].imageData)

	def resizeGL(self,width,height):
		pass

	def initializeGL(self):
		#glColor3f(0.0, 1.0, 1.0);
		#glViewport(0,0,500,500)
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();
		#glOrtho(-0.1, 20.0, 0.0, 10.0, 0.0, 10.0);
		glOrtho(-0.1, 1.0, -1.0, 5.0, 0.0, 10.0)
		#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		#glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		#glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

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
