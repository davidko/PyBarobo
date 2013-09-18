#!/usr/bin/env python

import serial
import time
import array
import Queue
import threading
import struct
import math
import socket

def deg2rad(deg):
  return deg*math.pi/180.0

def rad2deg(rad):
  return rad*180.0/math.pi

class BaroboException(Exception):
  def __init__(self, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)

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
  CMD_SETMOTORSTATES = 0x81

  MOTOR_FORWARD = 1
  MOTOR_BACKWARD = 2

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
    self.scannedIDs_cond = threading.Condition()
    pass

  def __init_comms(self):
    self.commsInThread = threading.Thread(target=self._commsInEngine)
    self.commsInThread.daemon = True
    self.commsInThread.start()
    self.commsOutThread = threading.Thread(target=self._commsOutEngine)
    self.commsOutThread.daemon = True
    self.commsOutThread.start()

  def addLinkbot(self, linkbot):
    self.children.append(linkbot)

  def connect(self):
    # Try to connect to BaroboLink running on localhost
    self.phys = PhysicalLayer_Socket('localhost', 5768)
    self.link = LinkLayer_Socket(self.phys, self.handlePacket)
    self.link.start()
    self.__init_comms()

  def connectDongleTTY(self, ttyfilename):
    self.phys = PhysicalLayer_TTY(ttyfilename)
    self.link = LinkLayer_TTY(self.phys, self.handlePacket)
    self.link.start()
    self.__init_comms()
    self.__getDongleID()

  def handlePacket(self, packet):
    self.readQueue.put(packet)

  def scanForRobots(self):
    buf = [ self.CMD_QUERYADDRESSES, 3, 0x00 ]
    self.writePacket(Packet(buf, 0x0000))

  def getScannedRobots(self):
    return self.scannedIDs

  def getLinkbot(self, serialID):
    if serialID not in self.scannedIDs:
      self.findRobot(serialID)
      self.waitForRobot(serialID)
    linkbot = Linkbot(self.scannedIDs[serialID], serialID, self)
    self.children.append(linkbot)
    return linkbot

  def findRobot(self, serialID):
    if serialID in self.scannedIDs:
      return
    buf = bytearray([ self.CMD_FINDMOBOT, 7 ])
    buf += bytearray(serialID)
    buf += bytearray([0])
    self.writePacket(Packet(buf, 0x0000))

  def waitForRobot(self, serialID, timeout=2.0):
    self.scannedIDs_cond.acquire()
    while serialID not in self.scannedIDs:
      self.scannedIDs_cond.wait(2)
    self.scannedIDs_cond.release()
    return serialID in self.scannedIDs

  def writePacket(self, packet):
    self.writeQueue.put(packet)

  def _commsInEngine(self):
    while True:
      packet = self.readQueue.get(block=True, timeout=None)
      # First, see if these are "Report Address" events. We want to filter
      # those out and use them for our own purposes
      if packet.data[0] == self.EVENT_REPORTADDRESS:
        botid = struct.unpack('!4s', packet.data[4:8])[0]
        zigbeeAddr = struct.unpack('!H', packet[2:4])[0]
        if botid not in self.scannedIDs:
          self.scannedIDs_cond.acquire()
          self.scannedIDs[botid] = zigbeeAddr
          self.scannedIDs_cond.notify()
          self.scannedIDs_cond.release()
        continue
      elif packet.data[0] == self.EVENT_DEBUG_MSG:
        print packet.data[2:]
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

  def __getDongleID(self):
    buf = [ self.CMD_GETSERIALID, 3, 0x00 ]
    self.writePacket(Packet(buf, 0x0000))
    response = self.ctxReadQueue.get(block=True, timeout=2.0)
    serialID = struct.unpack('!4s', response[2:6])[0]
    buf = [self.CMD_GETADDRESS, 3, 0x00]
    self.writePacket(Packet(buf, 0x0000))
    response = self.ctxReadQueue.get(block=True, timeout=2.0)
    zigbeeAddr = struct.unpack('!H', response[2:4])[0]
    self.scannedIDs[serialID] = zigbeeAddr
    

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

class PhysicalLayer_Socket(socket.socket):
  def __init__(self, hostname, port):
    socket.socket.__init__(self)
    self.connect((hostname, port))

  def flush(self):
    pass
  def flushInput(self):
    pass
  def flushOutput(self):
    pass

  def read(self):
    # Read and return a single byte
    return self.recv(1)

  def write(self, packet):
    self.sendall(packet)

class LinkLayer_Base:
  def __init__(self, physicalLayer, readCallback):
    self.phys = physicalLayer
    self.deliver = readCallback
    self.writeLock = threading.Lock()

  def start(self):
    self.thread = threading.Thread(target=self._run)
    self.thread.daemon = True
    self.thread.start()

class LinkLayer_TTY(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    newpacket = bytearray([ packet[0],
                            len(packet)+5,
                            address>>8,
                            address&0x00ff,
                            1 ])
    newpacket += bytearray(packet)
    self.writeLock.acquire()
    #print "Send: {}".format(map(hex, newpacket))
    self.phys.write(newpacket)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        print "Recv: {}".format(map(hex, self.readbuf))
        zigbeeAddr = struct.unpack('!H', self.readbuf[2:4])[0]
        if self.readbuf[0] != BaroboCtx.EVENT_REPORTADDRESS:
          pkt = Packet(self.readbuf[5:-1], zigbeeAddr)
        else:
          pkt = Packet(self.readbuf, zigbeeAddr)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]

class LinkLayer_Socket(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    self.writeLock.acquire()
    print "Send: {}".format(map(hex, packet))
    self.phys.write(packet)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        print "Recv: {}".format(map(hex, self.readbuf))
        pkt = Packet(self.readbuf, 0x8000)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]


class Linkbot:
  def __init__(self, zigbeeAddr = None, serialID = None, baroboContext = None):
    self.responseQueue = Queue.Queue()
    self.eventQueue = Queue.Queue()
    self.readQueue = Queue.Queue()
    self.writeQueue = Queue.Queue()
    self.zigbeeAddr = zigbeeAddr
    self.serialID = serialID
    self.baroboCtx = baroboContext
    self.messageThread = threading.Thread(target=self.__messageThread)
    self.messageThread.daemon = True
    self.messageThread.start()
    self.messageLock = threading.Lock()

  def connect(self):
    # Connect to a running instance of BaroboLink
    # First, make sure we have a BaroboCtx
    self.zigbeeAddr = 0x8000
    if not self.baroboCtx:
      self.baroboCtx = BaroboCtx()
      self.baroboCtx.connect()
      self.baroboCtx.addLinkbot(self)
    self.getSerialID()


  def setBuzzerFrequency(self, freq):
    buf = bytearray([0x6A, 0x05, (freq>>8)&0xff, freq&0xff, 0x00])
    self.__transactMessage(buf)

  def setLEDColor(self, r, g, b):
    buf = bytearray([BaroboCtx.CMD_RGBLED, 8, 0xff, 0xff, 0xff, r, g, b, 0x00])
    self.__transactMessage(buf)

  def moveTo(self, angle1, angle2, angle3):
    angle1 = deg2rad(angle1)
    angle2 = deg2rad(angle2)
    angle3 = deg2rad(angle3)
    buf = bytearray([BaroboCtx.CMD_SETMOTORANGLESABS, 0x13])
    buf += bytearray(struct.pack('<4f', angle1, angle2, angle3, 0.0))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def smoothMoveTo(self, joint, accel0, accelf, vmax, angle):
    _accel0 = rad2deg(accel0)
    _accelf = rad2deg(accelf)
    _vmax = rad2deg(vmax)
    _angle = rad2deg(angle)
    buf = bytearray([BaroboCtx.CMD_SMOOTHMOVE, 20, joint])
    buf += bytearray(struct.pack('<4f', _accel0, _accelf, _vmax, _angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def moveWait(self):
    isMoving = True
    while isMoving:
      buf = bytearray([BaroboCtx.CMD_IS_MOVING, 3, 0])
      response = self.__transactMessage(buf)
      isMoving = response[2]
      if isMoving:
        time.sleep(0.1)

  def getADCVolts(self, adc):
    buf = bytearray([BaroboCtx.CMD_GETENCODERVOLTAGE, 4, adc, 0])
    response = self.__transactMessage(buf)
    voltage = struct.unpack('<f', response[2:6])[0]
    return voltage

  def getJointAngles(self):
    buf = bytearray([BaroboCtx.CMD_GETMOTORANGLESABS, 3, 0])
    response = self.__transactMessage(buf)
    angles = struct.unpack('<4f', response[2:18])
    return map(rad2deg, angles)

  def getVersion(self):
    buf = bytearray([BaroboCtx.CMD_GETVERSION, 3, 0])
    response = self.__transactMessage(buf)
    return response[2]

  def setMotorDir(self, joint, direction):
    buf = bytearray([BaroboCtx.CMD_SETMOTORDIR, 5, joint-1, direction, 0])
    self.__transactMessage(buf)

  def setMotorSpeed(self, joint, speed):
    _speed = deg2rad(speed)
    buf = bytearray([BaroboCtx.CMD_SETMOTORSPEED, 8, joint-1])
    buf += bytearray(struct.pack('<f', _speed))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def setMotorStates(self, directions, speeds):
    if len(directions) < 4:
      directions += [0]*(4-len(directions))
    if len(speeds) < 4:
      speeds += [0.0]*(4-len(speeds))
    speeds = map(deg2rad, speeds)
    buf = bytearray([BaroboCtx.CMD_SETMOTORSTATES, 23])
    buf += bytearray(directions)
    buf += bytearray(struct.pack('<4f', speeds[0], speeds[1], speeds[2], speeds[3]))
    buf += bytearray([0x00])
    self.__transactMessage(buf)
   
  def getSerialID(self):
    buf = bytearray([BaroboCtx.CMD_GETSERIALID, 3, 0])
    response = self.__transactMessage(buf) 
    botid = struct.unpack('!4s', response[2:6])[0]
    print botid
    self.serialID = botid
    return botid

  def __transactMessage(self, buf):
    self.messageLock.acquire()
    self.baroboCtx.writePacket(Packet(buf, self.zigbeeAddr))
    try:
      response = self.responseQueue.get(block=True, timeout = 2.0)
    except:
      self.messageLock.release()
      raise BaroboException('Did not receive response from robot.')
    if response[0] != BaroboCtx.RESP_OK:
      self.messageLock.release()
      raise BaroboException('Robot returned error status.')
    self.messageLock.release()
    return response

  def __messageThread(self):
    # Scan and act on incoming messages
    while True:
      pkt = self.readQueue.get(block=True, timeout=None)
      if (pkt[0] == BaroboCtx.RESP_OK) or \
         (pkt[0] == BaroboCtx.RESP_ERR) or \
         (pkt[0] == BaroboCtx.RESP_ALREADY_PAIRED):
        self.responseQueue.put(pkt)
      else:
        self.eventQueue.put(pkt)


if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()
  print linkbot.getVersion()
  for i in range(1,4):
    linkbot.setMotorSpeed(i, 120)
  while True:
    linkbot.moveTo(360, 0, -360)
    linkbot.moveWait()
    linkbot.moveTo(0, 0, 0)
    linkbot.moveWait()

  """
  while True:
    linkbot.setMotorStates([1, 0, 2, 0], [ 120, 0, 120, 0 ])
    time.sleep(2)
    linkbot.setMotorStates([2, 0, 1, 0], [ 120, 0, 120, 0 ])
    time.sleep(2)
  """

  """
  time.sleep(1.5)
  ctx.scanForRobots()
  ctx.findRobot('ZK53')
  linkbot = ctx.getLinkbot('ZK53')
  print hex(linkbot.zigbeeAddr)
  linkbot.setLEDColor(0xff, 0, 0)
  time.sleep(0.5)
  linkbot.setLEDColor(0x0, 0xff, 0xff)
  linkbot.moveTo(0, 0, 0)
  linkbot.moveWait()
  print linkbot.getJointAngles()
  time.sleep(2)
  print ctx.getScannedRobots()
  """
