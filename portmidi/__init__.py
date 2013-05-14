# -*- coding: utf-8 -*-
import atexit
import ctypes as C
from portmidi.impl import Pm_GetDeviceInfo, Pm_Terminate, Pm_Initialize, Pm_DeviceInfo, Pm_OpenInput, Pm_Stream, Pm_CountDevices, raise_on_error, Pm_Event, Pm_Poll, Pm_Read, Pm_WriteShort, Pm_OpenOutput


def initialize():
	""" Initialize PortMidi. Must be called before any other library function or they'll likely fail. """
	raise_on_error(Pm_Initialize())
	atexit.register(terminate)


def terminate():
	""" Close PortMidi. Not strictly necessary. """
	raise_on_error(Pm_Terminate())


def describe_devices():
	""" Return a dictionary containing dictionaries describing the MIDI devices available. Any one of these dictionaries may be passed to open_*(). """
	out = {}
	for device_id in xrange(Pm_CountDevices()):
		di = Pm_GetDeviceInfo(device_id).contents
		out[device_id] = out_di = {"id": device_id}
		for key, _ in Pm_DeviceInfo._fields_:
			out_di[key] = getattr(di, key)
	return out


def find_device_by_spec(name_substring="", min_outputs=0, min_inputs=0):
	""" Find a device matching the given specs. """
	name_substring = name_substring.lower()
	for dev in describe_devices().itervalues():
		if name_substring in dev["name"].lower() and dev["n_outputs"] >= min_outputs and dev["n_inputs"] >= min_inputs:
			return dev


class InputStream(Pm_Stream):
	""" An input stream of MIDI events. This should not be constructed manually - use open_input() instead. """

	def __init__(self, *args, **kwargs):
		self.buffer_size = kwargs.pop("buffer_size", 128)
		self.event_buffer = (Pm_Event * self.buffer_size)()
		self.event_buffer_ptr = C.cast(self.event_buffer, C.POINTER(Pm_Event))
		super(InputStream, self).__init__(*args, **kwargs)

	def poll(self):
		""" Return True if there are events to read. """
		pm_error = raise_on_error(Pm_Poll(self))
		return bool(pm_error)

	def read(self):
		""" Return a list of Pm_Event objects describing the MIDI events read.
		The list returned will be overwritten by the next invocation of this function. """
		n_read = Pm_Read(self, self.event_buffer_ptr, self.buffer_size)
		if n_read < 0:
			raise_on_error(n_read)
		return self.event_buffer[:n_read]


class OutputStream(Pm_Stream):
	""" An output stream of MIDI events. This should not be constructed manually - use open_output() instead. """

	def write_midi_message(self, message, param1, param2, timestamp=0):
		""" Write a simple three-byte MIDI message into the stream. """
		msg = (message & 0xFF) | ((param1 & 0xFF) << 8) | ((param2 & 0xFF) << 16)
		Pm_WriteShort(self, timestamp, msg)


def open_input(device_id, latency=0):
	""" Open the input device described by the given ID. """
	if isinstance(device_id, dict) and device_id.get("id") is not None:
		device_id = device_id["id"]

	stream = InputStream()
	raise_on_error(Pm_OpenInput(C.pointer(stream), device_id, 0, latency, 0, 0))
	return stream


def open_output(device_id, latency=0):
	""" Open the output device described by the given ID. """
	if isinstance(device_id, dict) and device_id.get("id") is not None:
		device_id = device_id["id"]

	stream = OutputStream()
	raise_on_error(Pm_OpenOutput(C.pointer(stream), device_id, 0, latency, 0, 0))
	return stream

