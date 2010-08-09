# nxt.motor module -- Class to control LEGO Mindstorms NXT motors

PORT_A								= 0x00
PORT_B								= 0x01
PORT_C								= 0x02
PORT_AB								= 0x03
PORT_AC								= 0x04
PORT_BC								= 0x05
PORT_ABC							= 0xFF
PORT_ALL							= 0xFF

MODE_IDLE							= 0x00
MODE_MOTOR_ON						= 0x01
MODE_BRAKE							= 0x02
MODE_REGULATED						= 0x04

REGULATION_IDLE						= 0x00
REGULATION_MOTOR_SPEED				= 0x01
REGULATION_MOTOR_SYNC				= 0x02

RUN_STATE_IDLE						= 0x00
RUN_STATE_RAMP_UP					= 0x10
RUN_STATE_RUNNING					= 0x20
RUN_STATE_RAMP_DOWN					= 0x40

LIMIT_RUN_FOREVER					= 0

class Motor(object):

	def __init__(self, brick, port):
		self.brick					= brick
		self.port					= port
		self.power					= 0
		self.mode					= MODE_IDLE
		self.regulation				= REGULATION_IDLE
		self.turn_ratio				= 0
		self.run_state				= RUN_STATE_IDLE
		self.tacho_limit			= LIMIT_RUN_FOREVER
		self.tacho_count			= 0
		self.block_tacho_count		= 0
		self.rotation_count			= 0
		self.reply					= True

	# Send the telegram packet to the NXT brick
	def _set_state(self, port=PORT_A):
		self.brick.set_output_state(
			port,
			self.power,
			self.mode,
			self.regulation,
			self.turn_ratio,
			self.run_state,
			self.tacho_limit)

	def set_output_state(self):
		# FIXME: Convert to bitwise
		# Check which motors I need to send the command to
		if self.port == PORT_A:
			self._set_state(0x00)
		elif self.port == PORT_B:
			self._set_state(0x01)
		elif self.port == PORT_C:
			self._set_state(0x02)
		elif self.port == PORT_AB:
			self._set_state(0x00)
			self._set_state(0x01)
		elif self.port == PORT_AC:
			self._set_state(0x00)
			self._set_state(0x02)
		elif self.port == PORT_BC:
			self._set_state(0x01)
			self._set_state(0x02)
		elif self.port == PORT_ALL:
			self._set_state(0xFF)
		elif self.port == PORT_ABC:
			self._set_state(0xFF)
		else:
			# We didnt recognise the port, raise an error
			self.reply				= True
			self._set_state(0x99)

	def get_output_state(self):
		values						= self.brick.get_output_state(self.port)

		(self.port,
		self.power,
		self.mode,
		self.regulation,
		self.turn_ratio,
		self.run_state,
		self.tacho_limit,
		tacho_count,
		block_tacho_count,
		rotation_count)				= values
		return values

	def reset_position(self, relative):
		# We need to check if we have 0xFF for the drive.
		# If we do, we will get an out-of-range error.
		if self.port == PORT_A or self.port == PORT_B or self.port == PORT_C:
			self.brick.reset_motor_position(self.port, relative)
		elif self.port == PORT_AB:
			self.brick.reset_motor_position(PORT_A, relative)
			self.brick.reset_motor_position(PORT_B, relative)
		elif self.port == PORT_AC:
			self.brick.reset_motor_position(PORT_A, relative)
			self.brick.reset_motor_position(PORT_C, relative)
		elif self.port == PORT_BC:
			self.brick.reset_motor_position(PORT_B, relative)
			self.brick.reset_motor_position(PORT_C, relative)

		elif self.port == (PORT_ABC or PORT_ALL):
			self.brick.reset_motor_position(0x00, relative)
			self.brick.reset_motor_position(0x01, relative)
			self.brick.reset_motor_position(0x02, relative)
		else:
			self.reply				= True
			self.brick.reset_motor_position(0x99, relative)
