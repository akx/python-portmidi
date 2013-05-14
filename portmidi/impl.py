# -*- coding: utf-8 -*-
import ctypes as C
import sys
from portmidi.excs import PMError, PMHostError

if sys.platform == "win32":
	lib = C.cdll.LoadLibrary("portmidi.dll")
else:
	lib = C.cdll.LoadLibrary("portmidi.so")  # XXX: Untested.

def Func(name, arg_types=None, restype=C.c_int):
	if arg_types is None:
		arg_types = []
	f = getattr(lib, name)
	f.argtypes = arg_types
	f.restype = restype
	return f

Pm_HasHostError = Func("Pm_HasHostError", [C.c_void_p], C.c_int)
Pm_GetHostErrorText = Func("Pm_GetHostErrorText", [C.c_char_p, C.c_uint])
Pm_GetErrorText = Func("Pm_GetErrorText", [C.c_int], C.c_char_p)
Pm_Initialize = Func("Pm_Initialize")
Pm_Terminate = Func("Pm_Terminate")

def raise_on_error(pm_error):
	if not (pm_error == 0 or pm_error == 1):
		raise PMError("Error %d (%s)" % (pm_error, Pm_GetErrorText(pm_error)))
	return pm_error

def raise_on_host_error(stream):
	if Pm_HasHostError(stream):
		buf = C.create_string_buffer(256)
		Pm_GetHostErrorText(buf, 256)
		raise PMHostError("Host Error (%s)" % buf.value)



class Pm_DeviceInfo(C.Structure):
	_fields_ = [
		("structVersion", C.c_int),
		("interface", C.c_char_p),
		("name", C.c_char_p),
		("n_inputs", C.c_int),
		("n_outputs", C.c_int),
		("opened", C.c_bool),
	]

Pm_GetDeviceInfo = Func("Pm_GetDeviceInfo", [C.c_int], C.POINTER(Pm_DeviceInfo))
Pm_CountDevices = Func("Pm_CountDevices")

class Pm_Event(C.Structure):
	_fields_ = [
		("message", C.c_int32),
		("timestamp", C.c_int32),
	]

	def __str__(self):
		return "%08x (@t%010d)" % (self.message, self.timestamp)

	def _get_midi_fields(self):
		return (self.message & 0xFF), (self.message >> 8) & 0xFF, (self.message >> 16) & 0xFF

	midi_fields = property(_get_midi_fields)

class Pm_Stream(C.c_void_p):
	def close(self):
		raise_on_error(Pm_Close(self))

	def abort(self):
		raise_on_error(Pm_Abort(self))


Pm_Close = Func("Pm_Close", [Pm_Stream], C.c_int)
Pm_Abort = Func("Pm_Abort", [Pm_Stream], C.c_int)
Pm_Read = Func("Pm_Read", [Pm_Stream, C.POINTER(Pm_Event), C.c_int32], C.c_int)
Pm_Poll = Func("Pm_Poll", [Pm_Stream], C.c_int)
Pm_Write = Func("Pm_Write", [Pm_Stream, C.POINTER(Pm_Event), C.c_int32], C.c_int)
Pm_WriteShort = Func("Pm_WriteShort", [Pm_Stream, C.c_int32, C.c_int32], C.c_int)
Pm_OpenInput = Func("Pm_OpenInput", [C.POINTER(Pm_Stream), C.c_int, C.c_void_p, C.c_int32, C.c_void_p, C.c_void_p],
                    C.c_int)
Pm_OpenOutput = Func("Pm_OpenOutput", [C.POINTER(Pm_Stream), C.c_int, C.c_void_p, C.c_int32, C.c_void_p, C.c_void_p],
                     C.c_int)