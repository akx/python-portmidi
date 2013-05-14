# coding=utf-8

import OSC, portmidi


class MIDIToOSC(object):
	def __init__(self, midi_device_info, osc_server, cc_range, osc_prefix, osc_cc_path, debug=False):
		self.midi_device_info = midi_device_info
		self.cc_range = cc_range
		self.osc_prefix = osc_prefix
		self.osc_cc_path = osc_cc_path
		self.osc_server = osc_server
		self.debug = debug

	def open(self):
		self.osc_client = OSC.OSCClient()
		self.osc_client.connect(self.osc_server)
		self.input_stream = portmidi.open_input(self.midi_device_info, 0)

	def send(self, osc_message):
		if self.debug:
			print osc_message
		self.osc_client.send(osc_message)

	def process(self):
		for event in self.input_stream.read():
			msg, p1, p2 = event.midi_fields
			if msg & 176:  # Control change -- the only supported thing at the moment
				controller_num = (msg & 0xF) << 7 | p1
				controller_val = float(p2 / 127.0 * self.cc_range)
				osc_message = OSC.OSCMessage("%s%s/%s" % (self.osc_prefix, self.osc_cc_path, controller_num))
				osc_message.append(controller_val, "f")
				self.send(osc_message)


def cmd():
	import argparse

	ap = argparse.ArgumentParser()
	ap.add_argument("--device-name", default="")
	ap.add_argument("--osc-server", default="127.0.0.1:10101")
	ap.add_argument("--osc-cc-range", default=127, type=float)
	ap.add_argument("--osc-prefix", default="/mto")
	ap.add_argument("--osc-cc-path", default="/cc")
	ap.add_argument("--debug", "-d", action="store_true", default=False)

	args = ap.parse_args()

	try:
		host, s_port = str(args.osc_server).split(":")
		port = int(s_port)
	except:
		ap.error("Unable to parse server spec (try host:port)")
		return

	portmidi.initialize()
	dev = portmidi.find_device_by_spec(args.device_name, min_inputs=1)

	if not dev:
		ap.error("Couldn't find an appropriate MIDI device")

	mto = MIDIToOSC(
		midi_device_info=dev,
		osc_server=(host, port),
		cc_range=args.osc_cc_range,
		osc_prefix=args.osc_prefix,
		osc_cc_path=args.osc_cc_path,
		debug=bool(args.debug)
	)
	print "Starting processing (device %s)." % dev["name"]
	mto.open()
	while 1:
		mto.process()


if __name__ == "__main__":
	cmd()