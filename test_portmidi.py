# -*- coding: utf-8 -*-
import portmidi, time

portmidi.initialize()

dev = portmidi.find_device_by_spec("nanokontrol", min_inputs=1)
print dev
istrm = portmidi.open_input(dev)
print istrm

end_time = time.time() + 15

while time.time() < end_time:
	for ev in istrm.read():
		print ev, ev.midi_fields
	time.sleep(0.2)

istrm.close()
