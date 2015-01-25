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

radio = NRF24()
radio.begin(0, 0, 12)
radio.setRetries(15,15)
#radio.setPayloadSize(16)
radio.setChannel(0x4c)
radio.enableDynamicPayloads()
#radio.enableAckPayload()
radio.setAutoAck(True)

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_LOW)

radio.openWritingPipe(pipe_w)
radio.openReadingPipe(1, pipe_r)

radio.startListening()
radio.stopListening()

radio.printDetails()

#while True:
#	buf = [random.randint(10,20)]
#    radio.write(buf)
#    time.sleep(1)

# read
# definir RecvPayload como un array de 32 bytes.
#if (radio.available()):
	#done=false
	#while (!done):
		#len=radio.getDynamicPayloadSize();
		#done=radio.read(&RecvPayload,len);
	# terminar con un cero el array

def send(radio,msg):
	radio.stopListening()
	r=radio.write(msg);
	radio.startListening()
	return r;
def recv(radio,buf):
	if radio.available():
		ps=radio.getDynamicPayloadSize()
		radio.read(buf,ps)
		s=string.join(map(unichr,buf),'')
	else:
		"no data available"

