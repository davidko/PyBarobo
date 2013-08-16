#!/usr/bin/env python

import serial
import time
import array
import Queue
import threading
import struct

class BaroboCtx:
  RESP_OK = 0x10
  RESP_END = 0x11
  RESP_ERR = 0xff
  RESP_ALREADY_PAIRED = 0xfe

  EVENT_BUTTON = 0x20
  EVENT_REPORTADDRESS = 0x21
  EVENT_DEBUG_MSG = 0x22

  CMD_STATUS = 0x30
  CMD_DEMO = 0x31
  CMD_SETMOTORDIR = 0x32
  CMD_GETMOTORDIR = 0x33
  CMD_SETMOTORSPEED = 0x34
  CMD_GETMOTORSPEED = 0x35
  CMD_SETMOTORANGLES = 0x36
  CMD_SETMOTORANGLESABS = 0x37
  CMD_SETMOTORANGLESDIRECT = 0x38
  CMD_SETMOTORANGLESPID = 0x39
  CMD_GETMOTORANGLES = 0x3A
  CMD_GETMOTORANGLESABS = 0x3B
  CMD_GETMOTORANGLESTIMESTAMP = 0x3C
  CMD_GETMOTORANGLESTIMESTAMPABS = 0x3D
  CMD_SETMOTORANGLE = 0x3E
  CMD_SETMOTORANGLEABS = 0x3F
  CMD_SETMOTORANGLEDIRECT = 0x40
  CMD_SETMOTORANGLEPID = 0x41
  CMD_GETMOTORANGLE = 0x42
  CMD_GETMOTORANGLEABS = 0x43
  CMD_GETMOTORANGLETIMESTAMP = 0x44
  CMD_GETMOTORSTATE = 0x45
  CMD_GETMOTORMAXSPEED = 0x46
  CMD_GETENCODERVOLTAGE = 0x47
  CMD_GETBUTTONVOLTAGE = 0x48
  CMD_GETMOTORSAFETYLIMIT = 0x49
  CMD_SETMOTORSAFETYLIMIT = 0x4A
  CMD_GETMOTORSAFETYTIMEOUT = 0x4B
  CMD_SETMOTORSAFETYTIMEOUT = 0x4C
  CMD_STOP = 0x4D
  CMD_GETVERSION = 0x4E
  CMD_BLINKLED = 0x4F
  CMD_ENABLEBUTTONHANDLER = 0x50
  CMD_RESETABSCOUNTER = 0x51
  CMD_GETHWREV = 0x52
  CMD_SETHWREV = 0x53
  CMD_TIMEDACTION = 0x54
  CMD_GETBIGSTATE = 0x55
  CMD_SETFOURIERCOEFS = 0x56
  CMD_STARTFOURIER = 0x57
  CMD_LOADMELODY = 0x58
  CMD_PLAYMELODY = 0x59
  CMD_GETADDRESS = 0x5A
  CMD_QUERYADDRESSES = 0x5B
  CMD_GETQUERIEDADDRESSES = 0x5C
  CMD_CLEARQUERIEDADDRESSES = 0x5D
  CMD_REQUESTADDRESS = 0x5E
  CMD_REPORTADDRESS = 0x5F
  CMD_REBOOT = 0x60
  CMD_GETSERIALID = 0x61
  CMD_SETSERIALID = 0x62
  CMD_SETRFCHANNEL = 0x63
  CMD_FINDMOBOT = 0x64
  CMD_PAIRPARENT = 0x65
  CMD_UNPAIRPARENT = 0x66
  CMD_RGBLED = 0x67
  CMD_SETMOTORPOWER = 0x68
  CMD_GETBATTERYVOLTAGE = 0x69
  CMD_BUZZERFREQ = 0x6A
  CMD_GETACCEL = 0x6B
  CMD_GETFORMFACTOR = 0x6C
  CMD_GETRGB = 0x6D
  CMD_PLACEHOLDER201303291416 = 0x6E
  CMD_PLACEHOLDER201304121823 = 0x6F
  CMD_PLACEHOLDER201304152311 = 0x70
  CMD_PLACEHOLDER201304161605 = 0x71
  CMD_PLACEHOLDER201304181705 = 0x72
  CMD_PLACEHOLDER201304181425 = 0x73
  CMD_SET_GRP_MASTER = 0x74
  CMD_SET_GRP_SLAVE = 0x75
  CMD_SET_GRP = 0x76
  CMD_SAVE_POSE = 0x77
  CMD_MOVE_TO_POSE = 0x78
  CMD_IS_MOVING = 0x79
  CMD_GET_MOTOR_ERRORS = 0x7A
  CMD_MOVE_MOTORS = 0x7B
  CMD_TWI_SEND = 0x7C
  CMD_TWI_RECV = 0x7D
  CMD_TWI_SENDRECV = 0x7E
  CMD_PLACEHOLDER201306271044 = 0x7F
  CMD_PLACEHOLDER201307101241 = 0x80

  def __init__(self):
    # Queue going to the robot
    self.writeQueue = Queue.Queue() 
    # Queue coming from the robot
    self.readQueue = Queue.Queue()
    # Queue coming from the robot intended for the content
    self.ctxReadQueue = Queue.Queue()
    self.link = None
    self.phys = None
    self.children = [] # List of Linkbots
    self.scannedIDs = {}
    pass

  def connectDongleTTY(self, ttyfilename):
    self.phys = PhysicalLayer_TTY(ttyfilename)
    self.link = LinkLayer_Dummy(self.phys, self.handlePacket)
    self.link.start()
    self.commsInThread = threading.Thread(target=self._commsInEngine)
    self.commsInThread.daemon = True
    self.commsInThread.start()
    self.commsOutThread = threading.Thread(target=self._commsOutEngine)
    self.commsOutThread.daemon = True
    self.commsOutThread.start()

  def handlePacket(self, packet):
    self.readQueue.put(packet)

  def scanForRobots(self):
    buf = [ self.CMD_QUERYADDRESSES, 3, 0x00 ]
    self.link.write(buf, 0)

  def getScannedRobots(self):
    return self.scannedIDs

  def _commsInEngine(self):
    while True:
      packet = self.readQueue.get(block=True, timeout=None)
      print "Got packet"
      # First, see if these are "Report Address" events. We want to filter
      # those out and use them for our own purposes
      if packet.data[0] == self.EVENT_REPORTADDRESS:
        botid = struct.unpack('!4s', packet.data[4:8])
        zigbeeAddr = struct.unpack('!H', packet[2:4])[0]
        if botid not in self.scannedIDs:
          self.scannedIDs[botid] = zigbeeAddr
        continue
      # Get the zigbee address from the packet 
      zigbeeAddr = packet.addr
      if 0 == zigbeeAddr:
        self.ctxReadQueue.put(packet)
        continue
      for linkbot in self.children:
        if zigbeeAddr == linkbot.zigbeeAddr:
          linkbot.readQueue.put(packet, block=True)
          break

  def _commsOutEngine(self):
    while True:
      packet = self.writeQueue.get()
      self.link.write(packet.data, packet.addr)

class Packet:
  def __init__(self, data=None, addr=None):
    self.data = data
    self.addr = addr

  def __getitem__(self, key):
    return self.data[key]

class PhysicalLayer_TTY(serial.Serial):
  def __init__(self, ttyfilename):
    serial.Serial.__init__(self, ttyfilename, baudrate=230400)
    self.timeout = None

class LinkLayer_Dummy:
  def __init__(self, physicalLayer, readCallback):
    self.phys = physicalLayer
    self.deliver = readCallback
    self.writeLock = threading.Lock()

  def write(self, packet, address):
    newpacket = bytearray([ packet[0],
                            len(packet)+5,
                            address>>8,
                            address&0x00ff,
                            1 ])
    newpacket += bytearray(packet)
    self.writeLock.acquire()
    print "Write: {}".format(map(hex, newpacket))
    self.phys.write(newpacket)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        zigbeeAddr = struct.unpack('!H', self.readbuf[2:4])[0]
        if self.readbuf[0] != BaroboCtx.EVENT_REPORTADDRESS:
          pkt = Packet(self.readbuf[5:-1], zigbeeAddr)
        else:
          pkt = Packet(self.readbuf, zigbeeAddr)
        print "Packet: {}".format(map(hex, self.readbuf))
        print "Packet: {} {}".format(map(hex, pkt.data), hex(pkt.addr))
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]

  def start(self):
    self.thread = threading.Thread(target=self._run)
    self.thread.daemon = True
    self.thread.start()

class Linkbot:
  def __init__(self):
    self.readQueue = Queue.Queue()
    self.writeQueue = Queue.Queue()
    self.zigbeeAddr = 0
    pass

  def connectTTY(self, ttyfilename):
    self.serialdevice = serial.Serial(ttyfilename, baudrate=230400)
    self.comms = _CommsEngine(self.serialdevice)

  def getID(self):
    buf = bytearray([0x61, 0x03, 0x00])
    recv = self.comms.start(buf, 7, self.zigbeeAddr)
    r = array.array('B', recv[2:6]).tostring()
    return r

  def setBuzzerFrequency(self, freq):
    buf = bytearray([0x6A, 0x05, (freq>>8)&0xff, freq&0xff, 0x00])
    recv = self.comms.start(buf, 3, self.zigbeeAddr)

  def setLEDColor(self, r, g, b):
    buf = bytearray([0x67, 0x08, 0xff, 0xff, 0xff, r, g, b, 0x00])
    recv = self.comms.start(buf, 3, self.zigbeeAddr)

  def setID(self, idstr):
    if len(idstr) != 4:
      raise Exception("The ID String must be an alphanumeric string containing 4 characters.")
    buf = bytearray([0x62, 0x07])
    buf += bytearray(idstr)
    buf += bytearray([0x00])
    recv = self.comms.start(buf, 3, self.zigbeeAddr)
  

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  time.sleep(0.5)
  ctx.scanForRobots()
  time.sleep(2)
  print ctx.getScannedRobots()
