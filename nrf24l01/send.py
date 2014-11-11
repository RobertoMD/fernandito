import time
import I2C
d=I2C.Device(0x23,1)

def retry(byte,times):
	s=0
	for i in range(1,times):
		try:
			print ' {1}'.format(byte,i),
			d.writeRaw8(byte)
			s=1
		except IOError,e:
			time.sleep(0.5*i)
		if s==1:
			print 'Ok'
			break;	
	if s==0:
		print 'Ko'
	return s

for i in range(0,50):
	print 'sending {0}'.format(i),
	retry(i,10)
