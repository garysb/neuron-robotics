""" This contains a set of functions to calculate the a probable outcome that
	will arise from the given income.
"""

from __future__ import division

# Bayesian probabilities

def arc(new, old, arc=2.0):
	""" The arc algorithm is used to create a simple convex arc. We do this by
		taking the old value, divide it by 2
	"""
	#FIXME: This doesnt work correctly when using numbers that arnt real
	if new == 1.0:
		return												((new-old)/arc)+old

	if new == 0.0:
		return												old - (1.0 - old)
