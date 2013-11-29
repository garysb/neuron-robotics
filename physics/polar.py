""" The polar library contains a set of functions to work with polar coords.
	The different functions allow us to do simple manipulations of our
	coordinates. Please remember, we only use radians NOT degrees.
"""

from __future__ import division
from math import cos, sin, sqrt, atan2

def to_cartesian(r,a):
	""" This function converts standard polar coordinates into cartesian coords
		When given an r,a pair, we return a xcoord and ycoord pair to the method
		that called it.
	"""
	x = r * cos(a)
	y = r * sin(a)

	return x,y

def add(r1,a1,r2,a2):
	""" This adds two polar coordinates together. In order to do this, we first
		convert both polar coordinates into cartesian coordinates. Then once we
		have our two cartesian pairs, we simply add the two x values and the y
		values, then convert back into polars.
	"""
	x1,y1 = to_cartesian(r1,a1)
	x2,y2 = to_cartesian(r2,a2)

	x = x1+x2
	y = x2+y2

	r = sqrt( x * x + y * y)
	a = atan2(y, x)

	return r,a

def subtract(r1,a1,r2,a2):
	""" This function removes the second radius and azimuth from the first pair
		In order to do this, we unfortunatly have to convert our values into
		cartesian values. Once we've done this, we simply subtract the values
		from each other and convert back to polar coordinates.
	"""
	x1,y1 = to_cartesian(r1,a1)
	x2,y2 = to_cartesian(r2,a2)

	x = x1-x2
	y = x2-y2

	r = sqrt( x * x + y * y)
	a = atan2(y, x)

	return r,a

def multiply(r,a,m):
	""" This function multiplies the location r,a by a factor of m. This is
		basically scaling the value by a m times.
	"""
	r *= m

	return r,a

def divide(r,a,d):
	""" Dividing polar coordinates is really easy. We only need to divide the
		radius value because the azimuth never changes when doing division and
		multiplication with polar coordinates.
	"""
	r /= m

	return r,a

