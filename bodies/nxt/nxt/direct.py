# nxt.direct module -- LEGO Mindstorms NXT direct telegrams

def _create(opcode,reply_req=True):
	'Create a simple direct telegram'
	from telegram import Telegram
	return Telegram(direct=True, opcode=opcode, reply_req=reply_req)

def start_program(opcode, fname):
	'Start running a program on the nxt'
	tgram = _create(opcode)
	tgram.add_filename(fname)
	return tgram

def _parse_simple(tgram):
	tgram.check_status()

def stop_program(opcode):
	return _create(opcode)

def play_sound_file(opcode, loop, fname):
	tgram = _create(opcode)
	tgram.add_u8(loop)
	tgram.add_filename(fname)
	return tgram

def play_tone(opcode, frequency, duration):
	'Play a tone at frequency (Hz) for duration (ms)'
	tgram = _create(opcode)
	tgram.add_u16(frequency)
	tgram.add_u16(duration)
	return tgram

def set_output_state(opcode, port, power, mode, regulation, turn_ratio,
    run_state, tacho_limit, reply_req=True):
	tgram = _create(opcode, reply_req=reply_req)
	tgram.add_u8(port)
	tgram.add_s8(power)
	tgram.add_u8(mode)
	tgram.add_u8(regulation)
	tgram.add_s8(turn_ratio)
	tgram.add_u8(run_state)
	tgram.add_u32(tacho_limit)
	return tgram

def set_input_mode(opcode, port, sensor_type, sensor_mode):
	tgram = _create(opcode)
	tgram.add_u8(port)
	tgram.add_u8(sensor_type)
	tgram.add_u8(sensor_mode)
	return tgram

def get_output_state(opcode, port):
	tgram = _create(opcode)
	tgram.add_u8(port)
	return tgram

def _parse_get_output_state(tgram):
	tgram.check_status()
	port = tgram.parse_u8()
	power = tgram.parse_s8()
	mode = tgram.parse_u8()
	regulation = tgram.parse_u8()
	turn_ratio = tgram.parse_s8()
	run_state = tgram.parse_u8()
	tacho_limit = tgram.parse_u32()
	tacho_count = tgram.parse_s32()
	block_tacho_count = tgram.parse_s32()
	rotation_count = tgram.parse_s32()
	return (port, power, mode, regulation, turn_ratio, run_state,
		tacho_limit, tacho_count, block_tacho_count, rotation_count)

def get_input_values(opcode, port):
	tgram = _create(opcode)
	tgram.add_u8(port)
	return tgram

def _parse_get_input_values(tgram):
	tgram.check_status()
	port = tgram.parse_u8()
	valid = tgram.parse_u8()
	calibrated = tgram.parse_u8()
	sensor_type = tgram.parse_u8()
	sensor_mode = tgram.parse_u8()
	raw_ad_value = tgram.parse_u16()
	normalized_ad_value = tgram.parse_u16()
	scaled_value = tgram.parse_s16()
	calibrated_value = tgram.parse_s16()
	return (port, valid, calibrated, sensor_type, sensor_mode, raw_ad_value,
		normalized_ad_value, scaled_value, calibrated_value)

def reset_input_scaled_value(opcode, port):
	tgram = _create(opcode)
	tgram.add_u8(port)
	return tgram

def message_write(opcode, inbox, message):
	print message
	tgram = _create(opcode)
	tgram.add_u8(inbox)
	tgram.add_u8(len(message) + 1)
	tgram.add_string(len(message), message)
	tgram.add_u8(0)
	return tgram

def reset_motor_position(opcode, port, relative, reply_req=True):
	tgram = _create(opcode, reply_req=reply_req)
	tgram.add_u8(port)
	tgram.add_u8(relative)
	return tgram

def get_battery_level(opcode):
	return _create(opcode)

def _parse_get_battery_level(tgram):
	tgram.check_status()
	millivolts = tgram.parse_u16()
	return millivolts

def stop_sound_playback(opcode):
	return _create(opcode)

def keep_alive(opcode):
	return _create(opcode)

def _parse_keep_alive(tgram):
	tgram.check_status()
	sleep_time = tgram.parse_u32()
	return sleep_time

def ls_get_status(opcode, port):
	'Get status of low-speed sensor (ultrasonic)'
	tgram = _create(opcode)
	tgram.add_u8(port)
	return tgram

def _parse_ls_get_status(tgram):
	tgram.check_status()
	n_bytes = tgram.parse_u8()
	return n_bytes

def ls_write(opcode, port, tx_data, rx_bytes):
	'Write a low-speed command to a sensor (ultrasonic)'
	tgram = _create(opcode)
	tgram.add_u8(port)
	tgram.add_u8(len(tx_data))
	tgram.add_u8(rx_bytes)
	tgram.add_string(len(tx_data), tx_data)
	return tgram

def ls_read(opcode, port):
	'Read a low-speed sensor value (ultrasonic)'
	tgram = _create(opcode)
	tgram.add_u8(port)
	return tgram

def _parse_ls_read(tgram):
	tgram.check_status()
	n_bytes = tgram.parse_u8()
	contents = tgram.parse_string()
	return contents[:n_bytes]

def get_current_program_name(opcode):
	return _create(opcode)

def _parse_get_current_program_name(tgram):
	tgram.check_status()
	fname = tgram.parse_string()
	return fname

def message_read(opcode, remote_inbox, local_inbox, remove):
	tgram = _create(opcode)
	tgram.add_u8(remote_inbox)
	tgram.add_u8(local_inbox)
	tgram.add_u8(remove)
	return tgram

def _parse_message_read(tgram):
	tgram.check_status()
	local_inbox = tgram.parse_u8()
	n_bytes = tgram.parse_u8()
	message = tgram.parse_string()
	return (local_inbox, message[:n_bytes])

OPCODES = {
	0x00: (start_program, _parse_simple),
	0x01: (stop_program, _parse_simple),
	0x02: (play_sound_file, _parse_simple),
	0x03: (play_tone, _parse_simple),
	0x04: (set_output_state, _parse_simple),
	0x05: (set_input_mode, _parse_simple),
	0x06: (get_output_state, _parse_get_output_state),
	0x07: (get_input_values, _parse_get_input_values),
	0x08: (reset_input_scaled_value, _parse_simple),
	0x09: (message_write, _parse_simple),
	0x0A: (reset_motor_position, _parse_simple),
	0x0B: (get_battery_level, _parse_get_battery_level),
	0x0C: (stop_sound_playback, _parse_simple),
	0x0D: (keep_alive, _parse_keep_alive),
	0x0E: (ls_get_status, _parse_ls_get_status),
	0x0F: (ls_write, _parse_simple),
	0x10: (ls_read, _parse_ls_read),
	0x11: (get_current_program_name, _parse_get_current_program_name),
	0x13: (message_read, _parse_message_read),
}
