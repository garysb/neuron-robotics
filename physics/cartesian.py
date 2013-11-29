""" The cartesian library contains a set of functions to work with cartesian
	coordinates. The different functions allow us to do simple manipulations
	of our coordinates. Please remember, we only use radians NOT degrees.
"""

from __future__ import division
from math import sqrt, atan2, cos, sin

def to_polar(x,y):
	""" This function converts standard cartesian coordinates into polar coords
		When given an x,y pair, we return a radius and an azimuth to the method
		that called it.
	"""
	r = sqrt( x * x + y * y)
	a = atan2(y, x)
	return r,a

def add(x1,y1,x2,y2):
	""" This adds two cartesian coordinates together. Its really as simple as
		adding the two x values, and the two y values together.
	"""
	x = x1+x2
	y = x2+y2

	return x,y

def subtract(x1,y1,x2,y2):
	""" This function removes the second x,y pair from the first x,y pair. It
		simply subtracts x2 from x1 and subtracts y2 from y1, and then returns
		the new x,y pair. There is also a difference function that calculates
		the center x,y position in between the two x,y pairs.
	"""
	x = x1-x2
	y = y1-y2
	return x,y

def difference(x1,y1,x2,y2):
	""" As mentioned within the subtract functions documentation, this function
		calculates the difference between the two x,y pairs. This lets you find
		the center point in between the two coordinates.
	"""
	x = (x1+x2)/2
	y = (y1+y2)/2

	return x,y

def multiply(x,y,m):
	""" This function multiplies the location x,y by a factor of m. This is
		basically scaling the value by a m times. In order to do this, we must
		first convert into polar coordinates, then convert back into cartesian.
	"""
	r,a = to_polar(x,y)
	r *= m
	x = r * cos(a)
	y = r * sin(a)

	return x,y

def divide(x,y,d):
	""" When we divide cartesian values, we need to first convert the values
		into polar coordinates. Once we have our radius and azimuth, we then
		divide the radius by the divisor and convert back into our cartesian
		coordinates to get returned.
	"""
	r,a = to_polar(x,y)
	r /= m
	x = r * cos(a)
	y = r * sin(a)

	return x,y

