# -*- coding: utf-8 -*-
class PMError(Exception):
	""" A general PortMidi error. """
	pass

class PMHostError(Exception):
	""" A PortMidi host system error. """
	pass
