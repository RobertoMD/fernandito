#!/usr/bin/python
import RPi.GPIO as gpio
import time

class STEPPER:
	def __init__(self,steps=4,debug=True):
		self.debug=debug
		self.delay=None
		self.PINS=[22,21,18,17]
		if steps==4:
			if self.debug:
				print "4-step instance"
			self.FWD  =[(22,),(21,),(18,),(17,)]
			self.FWD  =[(17,),(18,),(21,),(22,)]
			self.delay = 0.05
		else:
			if self.debug:
				print "8-step instance"
			self.FWD = [(22,),(22,21),(21,),(21,18),(18,),(18,17),(17,),(17,22)]
			self.REV = [(17,),(17,18),(18,),(18,21),(21,),(21,22),(22,),(22,17)]
			self.delay = 0.002
		self.__setupgpio__()
	def __setupgpio__(self):
		gpio.setmode(gpio.BCM)
		for pin in self.PINS:
			gpio.setup(pin, gpio.OUT)
	def disable(self):
		gpio.cleanup()
	def enable(self):
		self.__setupgpio__()
	def _step_(self,sequence):
		for step in sequence:
			for pin in self.PINS:
				gpio.output(pin, gpio.HIGH) if pin in step else gpio.output(pin, gpio.LOW)
			time.sleep(self.delay)
	def forward(self,steps):
		for i in range(0,steps):
			self._step_(self.FWD)
	def reverse(self,steps):
		for i in range(0,steps):
			self._step_(self.REV)
	def setdelay(self,delay):
		self.delay=delay
