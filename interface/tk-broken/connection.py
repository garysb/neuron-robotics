# Import the ardrone network

def create(unique='00:16:53:01:AD:F3'):
	# Check we have a valid address to bind to
	#if not bluetooth.is_valid_address(unique):
	#	return {}

	# Find and connect to the lego nxt
	# try:
	if True:
		con													= {}
		con['id']											= unique
		con['sock']											= False
		con['con']											= con['sock']

	#except bodies.nxt.nxt.locator.BrickNotFoundError:
	#	return {}

	return con
