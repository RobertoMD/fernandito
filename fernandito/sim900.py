import sys,os,serial,threading,logging,time

LF = serial.to_bytes([0x0A])
CR = serial.to_bytes([0x0D])
CRLF = serial.to_bytes([13, 10])
PORT  = '/dev/ttyAMA0'
SPEED = 19200

logging.basicConfig(stream=sys.stderr,level=logging.DEBUG)
class SIM900():
	def __init__(self,port=PORT,baudrate=SPEED):
		self._readbuffer=''
		try:
			self.serial=serial.Serial(port,baudrate)
			logging.debug('Serial port open')
			self.start()
		except Exception:
			logging.debug('Cannot open serial port')
			self.serial=None
	def start(self):
		logging.debug('Serial Read enabled')
		self._readenabled=True
		# reception thread
		self.rthread = threading.Thread(target=self.reader)
		self.rthread.daemon=True
		self.rthread.start()

	def stop(self):
		logging.debug('Serial Read disabled')
		self._readenabled=False
		self.rthread.join()

	def getdata(self):
		r=self._readbuffer
		self._readbuffer=''
		return r

	def peekdata(self):
		return self._readbuffer

	def cleardata(self):
		self._readbuffer=''

	def reader(self):
		"""loop and copy serial->console"""
		try:
			while self._readenabled:
				if self.serial.inWaiting()>0:
					data=self.serial.read(self.serial.inWaiting())
					logging.debug('Read '+repr(len(data))+' bytes')
					self._readbuffer+=data
					sys.stderr.flush()
				else:
					time.sleep(1)
		except serial.SerialException, e:
			self._readenabled = False
			logging.debug('Exception reading serial data. Disabling read')
			# would be nice if the console reader could be interrupted at this
			# point...
			raise
 
	def writeline(self,s):
		self.serial.write(s+CRLF)
		self.serial.flush()
		logging.debug('> '+s)
		sys.stderr.flush()

	def write(self,data):
		self.serial.write(data)
		self.serial.flush()	
		logging.debug('> '+data)
		sys.stderr.flush()

	def command(self,s,timeout=1):
		self.cleardata()
		logging.debug('> Command '+s)
		self.serial.write(s+CRLF)
		#self.serial.flush()
		# wait for answer to arrive
		while len(self.peekdata())==0:
			time.sleep(0.5)
		time.sleep(timeout)
		l=self.getdata().replace('\r','').split('\n')
		# remove empty elements (empty lines)
		return [x for x in l if x]

