#!/usr/bin/env python

import threading
import time
import struct

from comms import *
from barobo import *
from util import *

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

  def moveToNB(self, angle1, angle2, angle3):
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

