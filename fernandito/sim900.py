import sys,os,serial,threading,logging,time
import shlex

LF = serial.to_bytes([0x0A])
CR = serial.to_bytes([0x0D])
CRLF = serial.to_bytes([13, 10])
EOF = serial.to_bytes([26])
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
			#SMS mode text
			self.command('AT+CMGF=1')
			self._awaitingdata=False
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
					logging.debug('<<< '+repr(len(data))+' bytes')
					#if answer to command is expected
					if self._awaitingdata:
						#append data to existing buffer
						self._readbuffer+=data
					#if oob received, process info and do not add this to the buffer
					else:
						self.processoobdata(data)
					sys.stderr.flush()
				else:
					time.sleep(1)
		except serial.SerialException, e:
			self._readenabled = False
			logging.debug('Exception reading serial data. Disabling read')
			# would be nice if the console reader could be interrupted at this
			# point...
			raise
 
	def processoobdata(self,data):
		d=data.strip('\r\n')
		# sms: '+CMTI: "SM",<index>'
		if d.startswith('+CMTI:'):
			self.processnewsms()
		# incoming call: RING
		elif d.startswith('RING'):
			self.incomingcall()
		# incoming call hung: NO CARRIER
		elif d.startswith('NO CARRIER'):
			self.incomingcallend()
		else:
			logging.debug('Unknown unsolicited data:'+data)
		pass

	def processnewsms(self):
		logging.debug('Processing new sms')
		return

	def incomingcall(self):
		logging.debug('Incoming call')
		return

	def incomingcallend(self):
		logging.debug('Incoming call ended')
		return

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

	def sendsms(self,dest,text):
		s='AT+CMGS="'+dest+'"'
		l=self.command(s)
		l=l+self.command(text)
		return l+self.command(EOF)

	def shutdownGSM(self):
		return self.command('AT+CPOWD=1')

	def command(self,s,timeout=1):
		self.cleardata()
		self._awaitingdata=True;
		logging.debug('>>> '+s)
		self.serial.write(s+CRLF)
		#self.serial.flush()
		# wait for answer to arrive
		while len(self.peekdata())==0:
			time.sleep(0.5)
		time.sleep(timeout)
		self._awaitingdata=False;
		l=self.getdata().replace('\r','').split('\n')
		# remove empty elements (empty lines)
		return [x for x in l if x]

	def getsms(self):
		r=self.command('AT+CMGL="ALL",1')
		l=[]
		#return if command did not end correctly
		if len(r)>0:
			if r[-1]=='OK':
				for i in range(1,len(r)-2,2):	
					e=r[i].replace('"','').split(',')
					e.append(r[i+1])
					l.append(e)
		return l
		
