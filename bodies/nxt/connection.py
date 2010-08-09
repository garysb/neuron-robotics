import bluetooth

# NXT Communication
import bodies.nxt.nxt.locator
import bodies.nxt.nxt.brick
import bodies.nxt.nxt.direct

def create(unique='00:16:53:01:AD:F3'):
	# Check we have a valid address to bind to
	if not bluetooth.is_valid_address(unique):
		return {}

	# Find and connect to the lego nxt
	try:
		con													= {}
		con['id']											= unique
		con['sock']											= bodies.nxt.nxt.locator.find_one_brick(host=unique)
		con['con']											= con['sock'].connect()

		# Make sure the nxt doesnt time out
		con['con'].keep_alive()
		con['con'].play_tone_and_wait(659, 250)
		con['con'].start_program('motors.rxe')

	except bodies.nxt.nxt.locator.BrickNotFoundError:
		return {}

	return con
