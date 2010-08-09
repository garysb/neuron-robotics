""" This module generates information partaining to information gathered from
	device feedback. Basically, it generates and proccesses information from it
	sensors and builds maps of its environment. It then parses the maps and
	tries to recognise objects around it and generates a profile of what objects
	are located where. Its broken into 3 different 'ranges'. Local awareness
	defines information from range sensors and uses this info to tell what
	is around it at the current point in time. Relative information is gathered
	to try get information about its current property (like a room or house).
	Global data uses gps to try remember where in the world a certain relative
	object is.
"""