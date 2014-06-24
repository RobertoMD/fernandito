import sys,os,serial,threading,logging,time
import shlex

LF = serial.to_bytes([0x0A])
CR = serial.to_bytes([0x0D])
CRLF = serial.to_bytes([13, 10])
EOF = serial.to_bytes([26])
PORT  = '/dev/ttyAMA0'
SPEED = 19200

logging.basicConfig(stream=sys.stderr,level=logging.INFO)

class SIM900():
	def __init__(self,port=PORT,baudrate=SPEED):
		self._readbuffer=''
		try:
			self._smscache=None
			self._awaitingdata=False
			self._imei=None
			# Open port
			self.serial=serial.Serial(port,baudrate)
			logging.debug('Serial port open')
			# Start read thread
			self.start()
			# SMS mode text
			self.command('AT+CMGF=1')
			# Not currently awaiting data
			# Create sms cache
			self.syncsms()
			# Get IMEI
			self._imei=self.command('AT+GSN')[1]
			self._imei=
			# Get incoming call info
			self.command('AT+CLCC=1')

		except Exception:
			logging.critical('Cannot open serial port')
			self.serial=None

	def start(self):
		logging.info('Serial Read enabled')
		self._readenabled=True
		# reception thread
		self.rthread = threading.Thread(target=self.reader)
		self.rthread.daemon=True
		self.rthread.start()

	def stop(self):
		logging.info('Serial Read disabled')
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
			logging.warning('Exception reading serial data. Disabling read')
			# would be nice if the console reader could be interrupted at this
			# point...
			raise
 
	def syncsms(self):
			logging.info('Copying SMS to local buffer')
			self._smscache=self.getsms()

	def processoobdata(self,data):
		#ojo pueden venir mas de una linea, por ejemplo al arrancar
		d=data.strip('\r\n')
		# sms: '+CMTI: "SM",<index>'
		if d.startswith('+CMTI:'):
			index=data.split(',')[1]
			self.processnewsms(index)
		elif d.startswith('+CLCC:'):
			self._callerid=d.split(',')[5].strip('"')
			self._callstatus=d.split(',')[2]  # 0-active, 1-held, 2-dialing (MO), 3-alerting (MO), 4-incoming (MT), 5-waiting(MT), 6-disconnect
			self._calltype=d.split(',')[3]    # 0-voice, 1-data, 2-fax
		# incoming call: RING
		elif d.startswith('RING'):
			self.incomingcall()
		# incoming call hung: NO CARRIER
		elif d.startswith('NO CARRIER'):
			self.incomingcallend()
		# *PSNWID: "214","03", "Orange", 0, "Orange", 0
		elif d.startswith('*PSNWID:'):
			pass
		#+COPS: (1,"movistar","movistar","21407"),(2,"simyo","","21403"),(1,"vodafone ES","voda ES","21401"),,(0,1,4),(0,1,2)
		elif d.startswith('+COPS:'):
			pass
		else:
			logging.info('Unknown unsolicited data:'+data)
		pass

	def processnewsms(self,index):
		self.syncsms()
		if type(index).__name__=='int':
			index=str(index)
		logging.info('Processing new sms')
		logging.debug('SMS Index: '+index)
		found=False
		for m in self._smscache:
			if m[0].split()[1]==index:
				found=True
				logging.info('Status:'+m[1])
				logging.info('Source:'+m[2])
				logging.info('Date  :'+m[4])
				logging.info('Time  :'+m[5])
				logging.info('Text  :'+m[6])
		if not found:
			logging.warning('SMS Index ',index,' not found')
		return

	def incomingcall(self):
		for i in l:
			print i

	def incomingcall(self):
		logging.info('Incoming call')
		return

	def incomingcallend(self):
		logging.info('Incoming call ended')
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

	def shutdown(self):
		return self.command('AT+CPOWD=1')

	def command(self,s,timeout=1):
		self.cleardata()
		self._awaitingdata=True;
		logging.info('>>> '+s)
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

	def iscmdok(self,data):
		if data[-1]=='OK':
			return True
		return False

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
		
