#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
from nrf24 import NRF24
import time,random,string

GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()
pipe_r=0xc2e6e6e6e6
pipe_w=0xe7e7e7e7e7

CMD_PING='P'
CMD_TEMP='T'
CMD_RANDOM='R'
CMD_VERBOSE='V'

radio = NRF24()
radio.begin(0, 0, 12)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x4c)
radio.enableDynamicPayloads()
#radio.enableAckPayload()
radio.setAutoAck(True)

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)

radio.openWritingPipe(pipe_w)
radio.openReadingPipe(1, pipe_r)

radio.startListening()
radio.stopListening()

radio.printDetails()

def send(radio,msg):
	radio.stopListening()
	r=radio.write(msg);
	radio.startListening()
	return r;
def recv(radio):
	b=[]
	if radio.available():
		ps=radio.getDynamicPayloadSize()
		radio.read(b,ps)
		s=string.join(map(unichr,b),'')
		return s
	else:
		print "no data available"
		return ''
def getTemp(radio):
	if (send(radio,'T') == 32):
		time.sleep(2)
		s=recv(radio)
	else:
		print "Unable to connect"
	return s
