#!/usr/bin/env python
import os
import sys
from cStringIO import StringIO
from math import sqrt
from qt import *
from opencv import cv
from opencv import highgui
from opencv import adaptors
import Image

class Visual(QWidget):
	def __init__(self, *args):
		apply(QWidget.__init__,(self, ) + args)
		self.cascade_name						= 'haarcascades/haarcascade_frontalface_alt.xml'
		self.cascade							= cv.cvLoadHaarClassifierCascade(self.cascade_name, cv.cvSize(20,20))
		self.storage							= cv.cvCreateMemStorage(0)
		self.cap								= highgui.cvCreateCameraCapture(0)
		self.q_buffer							= QImage()
		self.q_buffer.create(420,300,8)
		self.timer								= self.startTimer(1)

	def timerEvent(self, ev):
		# Fetch a frame from the video camera
		frame									= highgui.cvQueryFrame(self.cap)
		img_orig								= cv.cvCreateImage(cv.cvSize(frame.width,frame.height),cv.IPL_DEPTH_8U, frame.nChannels)
		if (frame.origin == cv.IPL_ORIGIN_TL):
			cv.cvCopy(frame, img_orig)
		else:
			cv.cvFlip(frame, img_orig, 0)

		# Create a grey frame to clarify data

		#img									= self.detect_face(frame_copy)
		img										= self.detect_squares(frame_copy)
		img_pil									= adaptors.Ipl2PIL(img)
		s										= StringIO()
		img_pil.save(s, "PNG")
		s.seek(0)
		q_img									= QImage()
		q_img.loadFromData(s.read())
		bitBlt(self, 0, 0, q_img)

	def paintEvent(self, ev):
		print 'paint'
		bitBlt(self, 0, 0, self.q_buffer)

	def resizeEvent(self, ev):
		pass

	def detect_face(self, img):
		""" Detect faces within an image, then draw around them.
			The default parameters (scale_factor=1.1, min_neighbors=3, flags=0) are tuned 
			for accurate yet slow object detection. For a faster operation on real video 
			images the settings are: 
			scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
			min_size=<minimum possible face size
		"""
		min_size								= cv.cvSize(20,20)
		image_scale								= 1.3
		haar_scale								= 1.2
		min_neighbors							= 2
		haar_flags								= 0
		gray									= cv.cvCreateImage(cv.cvSize(img.width,img.height), 8, 1)
		small_img								= cv.cvCreateImage(cv.cvSize(cv.cvRound(img.width/image_scale),
												  cv.cvRound(img.height/image_scale)), 8, 1)
		cv.cvCvtColor(img, gray, cv.CV_BGR2GRAY)
		cv.cvResize(gray, small_img, cv.CV_INTER_LINEAR)
		cv.cvEqualizeHist(small_img, small_img)
		cv.cvClearMemStorage(self.storage)

		if(self.cascade):
			t									= cv.cvGetTickCount();
			faces								= cv.cvHaarDetectObjects(small_img,
																		self.cascade,
																		self.storage,
																		haar_scale,
																		min_neighbors,
																		haar_flags,
																		min_size)
			t									= cv.cvGetTickCount() - t
			#print "detection time = %gms" % (t/(cvGetTickFrequency()*1000.));
			if faces:
				for r in faces:
					pt1							= cv.cvPoint(int(r.x*image_scale), int(r.y*image_scale))
					pt2							= cv.cvPoint(int((r.x+r.width)*image_scale),
																int((r.y+r.height)*image_scale))
					cv.cvRectangle(img, pt1, pt2, cv.CV_RGB(255,0,0), 3, 8, 0)
		return img

	def detect_squares(self, img):
		""" Find squares within the video stream and draw them """
		N										= 11
		thresh									= 5
		sz										= cv.cvSize(img.width & -2, img.height & -2)
		timg									= cv.cvCloneImage(img)
		gray									= cv.cvCreateImage(sz, 8, 1)
		pyr										= cv.cvCreateImage(cv.cvSize(sz.width/2, sz.height/2), 8, 3)
		# create empty sequence that will contain points -
		# 4 points per square (the square's vertices)
		squares									= cv.cvCreateSeq(0, cv.sizeof_CvSeq, cv.sizeof_CvPoint, self.storage)
		squares									= cv.CvSeq_CvPoint.cast(squares)

		# select the maximum ROI in the image
		# with the width and height divisible by 2
		subimage								= cv.cvGetSubRect(timg, cv.cvRect(0, 0, sz.width, sz.height))

		# down-scale and upscale the image to filter out the noise
		cv.cvPyrDown(subimage, pyr, 7)
		cv.cvPyrUp(pyr, subimage, 7)
		tgray									= cv.cvCreateImage(sz, 8, 1)
		# find squares in every color plane of the image
		for c in range(3):
			# extract the c-th color plane
			channels							= [None, None, None]
			channels[c]							= tgray
			cv.cvSplit(subimage, channels[0], channels[1], channels[2], None)
			for l in range(N):
				# hack: use Canny instead of zero threshold level.
				# Canny helps to catch squares with gradient shading
				if(l == 0):
					# apply Canny. Take the upper threshold from slider
					# and set the lower to 0 (which forces edges merging)
					cv.cvCanny(tgray, gray, 0, thresh, 5)
					# dilate canny output to remove potential
					# holes between edge segments
					cv.cvDilate(gray, gray, None, 1)
				else:
					# apply threshold if l!=0:
					#     tgray(x,y) = gray(x,y) < (l+1)*255/N ? 255 : 0
					cv.cvThreshold(tgray, gray, (l+1)*255/N, 255, cv.CV_THRESH_BINARY)

				# find contours and store them all as a list
				count, contours					= cv.cvFindContours(gray,
																	self.storage,
																	cv.sizeof_CvContour,
																	cv.CV_RETR_LIST,
																	cv.CV_CHAIN_APPROX_SIMPLE,
																	cv.cvPoint(0,0))

				if not contours:
					continue

				# test each contour
				for contour in contours.hrange():
					# approximate contour with accuracy proportional
					# to the contour perimeter
					result						= cv.cvApproxPoly(contour,
																	cv.sizeof_CvContour,
																	self.storage,
																	cv.CV_POLY_APPROX_DP,
																	cv.cvContourPerimeter(contours)*0.02, 0)
					# square contours should have 4 vertices after approximation
					# relatively large area (to filter out noisy contours)
					# and be convex.
					# Note: absolute value of an area is used because
					# area may be positive or negative - in accordance with the
					# contour orientation
					if(result.total == 4 and abs(cv.cvContourArea(result)) > 1000 and cv.cvCheckContourConvexity(result)):
						s						= 0
						for i in range(5):
							# find minimum angle between joint
							# edges (maximum of cosine)
							if(i >= 2):
								t				= abs(self.squares_angle(result[i], result[i-2], result[i-1]))
								if s<t:
									s			= t
						# if cosines of all angles are small
						# (all angles are ~90 degree) then write quandrange
						# vertices to resultant sequence
						if(s < 0.3):
							for i in range(4):
								squares.append(result[i])

		i										= 0
		while i<squares.total:
			pt									= []
			# read 4 vertices
			pt.append(squares[i])
			pt.append(squares[i+1])
			pt.append(squares[i+2])
			pt.append(squares[i+3])

			# draw the square as a closed polyline
			cv.cvPolyLine(img, [pt], 1, cv.CV_RGB(0,255,0), 3, cv.CV_AA, 0)
			i									+= 4

		return img

	def squares_angle(self, pt1, pt2, pt0):
		""" Calculate the angles of the squares """
		dx1										= pt1.x - pt0.x;
		dy1										= pt1.y - pt0.y;
		dx2										= pt2.x - pt0.x;
		dy2										= pt2.y - pt0.y;
		return (dx1*dx2 + dy1*dy2)/sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10);

	def detect_circles(self, img):
		""" Find circles within the video stream """
		

class MainWindow(QMainWindow):
	def __init__(self, *args):
		apply(QMainWindow.__init__, (self,) + args)
		self.visual								= Visual(self)
		self.setCentralWidget(self.visual)

def main(args):
	app											= QApplication(args)
	win											= MainWindow()
	win.show()
	app.connect(app, SIGNAL("lastWindowClosed()")
					, app
					, SLOT("quit()")
					)
	app.exec_loop()

if __name__=="__main__":
	main(sys.argv)
