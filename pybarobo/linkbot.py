#!/usr/bin/env python

import threading
import time
import struct

from comms import *
from barobo import *
from util import *

class Linkbot:
  """
  The Linkbot Class

  Each instance of this class can be used to represent a physical Linkbot. The
  member functions of this class can be used to get data, set motor angles,
  beep the buzzer, scan for button events, and more.  
  """

  def __init__(self):
    self.responseQueue = Queue.Queue()
    self.eventQueue = Queue.Queue()
    self.readQueue = Queue.Queue()
    self.writeQueue = Queue.Queue()
    self.zigbeeAddr = None
    self.serialID = None
    self.baroboCtx = None
    self.messageThread = threading.Thread(target=self.__messageThread)
    self.messageThread.daemon = True
    self.messageThread.start()
    self.messageLock = threading.Lock()

  def connect(self):
    """
    Connect to a Linkbot through BaroboLink
    """
    # Connect to a running instance of BaroboLink
    # First, make sure we have a BaroboCtx
    self.zigbeeAddr = 0x8000
    if not self.baroboCtx:
      self.baroboCtx = BaroboCtx()
      self.baroboCtx.connect()
      self.baroboCtx.addLinkbot(self)
    self.getSerialID()

  def disconnect(self):
    """
    Disconnect from the Linkbot.
    """
    buf = bytearray([BaroboCtx.CMD_UNPAIRPARENT, 3, 0])
    response = self.__transactMessage(buf)

  def driveJointTo(self, joint, angle):
    """
    Drive a single joint to a position as fast as possible, using the on-board
    PID motor controller.

    @type joint: number [1,3]
    @param joint: The joint to move
    @type angle: number
    @param angle: The angle to move the joint to, in degrees
    """
    self.driveJointToNB(self, joint, angle)
    self.moveWait()

  def driveJointToNB(self, joint, angle):
    """
    Non-blocking version of driveJointTo(). Please see driveJointTo() for more
    details.
    """
    buf = bytearray([BaroboCtx.CMD_SETMOTORANGLEPID, 0x08, joint])
    buf += bytearray(struct.pack('<f', angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def driveTo(self, angle1, angle2, angle3):
    """
    Drive the joints to angles as fast as possible using on-board PID
    controller.

    @type angle1: number
    @param angle1: Position to move the joint, in degrees
    @type angle2: number
    @param angle2: Position to move the joint, in degrees
    @type angle3: number
    @param angle3: Position to move the joint, in degrees
    """
    self.driveToNB(angle1, angle2, angle3)
    self.moveWait()

  def driveToNB(self, angle1, angle2, angle3):
    """
    Non-blocking version of driveTo(). See driveTo() for more details
    """
    buf = bytearray([BaroboCtx.CMD_SETMOTORANGLESPID, 0x13])
    buf += bytearray(struct.pack('<4f', angle1, angle2, angle3, 0.0))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def _getADCVolts(self, adc):
    buf = bytearray([BaroboCtx.CMD_GETENCODERVOLTAGE, 4, adc, 0])
    response = self.__transactMessage(buf)
    voltage = struct.unpack('<f', response[2:6])[0]
    return voltage

  def getAccelerometerData(self):
    """
    Get the current accelerometer readings

    @rtype: [number, number, number]
    @return: A list of acceleration values in the x, y, and z directions.
      Accelerometer values are in units of "G's", where 1 G is standard earth
      gravitational acceleration (9.8m/s/s)
    """
    buf = bytearray([BaroboCtx.CMD_GETACCEL, 0x03, 0x00])
    response = self.__transactMessage(buf)
    values = struct.unpack('<3h', response[2:8])
    return map(lambda x: x/16384.0, values)

  def getBatteryVoltage(self):
    """
    Get the current battery voltage of the Linkbot.

    @rtype: number
    @return: Returns a value in Volts
    """
    buf = bytearray([BaroboCtx.CMD_GETBATTERYVOLTAGE, 0x03, 0x00])
    response = self.__transactMessage(buf)
    voltage = struct.unpack('<f', response[2:6])[0]
    return voltage

  def getBreakoutADC(self, adc):
    """
    Get the ADC (Analog-to-digital) reading from a breakout-board's ADC
    channel. 

    @type adc: number
    @param adc: The ADC channel to get the value from [0, 7]
    @rtype: number
    @return: Volts
    """
    # set the ADC channel
    buf = bytearray([BaroboCtx.MSG_REGACCESS, 0x7C, 0x40|(adc&0x0f) ])
    self.twiSend(0x02, buf)
    # Start the conversion
    buf = bytearray([BaroboCtx.MSG_REGACCESS, 0x7A, 0xC7])
    self.twiSend(0x02, buf)
    # Get the result
    buf = bytearray([BaroboCtx.MSG_REGACCESS, 0x78])
    data = self.twiSendRecv(0x02, buf, 2) 
    return struct.unpack('<h', data)[0]

  def getColorRGB(self):
    """
    Get the current RGB values of the rgbled

    @rtype: [number, number, number]
    @return: The red, green, and blue values from 0 to 255
    """
    buf = bytearray([BaroboCtx.CMD_GETRGB, 0x03, 0x00])
    response = self.__transactMessage(buf)
    return struct.unpack('<3B', response[2:5])

  def getJointAngle(self, joint):
    """
    Get the current angle position of a joint.

    @type joint: number
    @param joint: Get the position of this joint. Can be 1, 2, or 3
    @rtype: number
    @return: Return the joint angle in degrees
    """
    buf = bytearray([BaroboCtx.CMD_GETMOTORANGLE, 0x04, joint, 0x00])
    response = self.__transactMessage(buf)
    return rad2deg(struct.unpack('<f', response[2:6])[0])

  def getJointAngles(self):
    """
    Get the current joint angles.

    @rtype: [float, float, float]
    @return: The joint angles in degrees
    """
    buf = bytearray([BaroboCtx.CMD_GETMOTORANGLESABS, 3, 0])
    response = self.__transactMessage(buf)
    angles = struct.unpack('<4f', response[2:18])
    return map(rad2deg, angles[:3])

  def getJointAnglesTime(self):
    """
    Get the joint angles with a timestamp. The timestamp is the number of
    seconds since the robot has powered on.

    @rtype: [numbers]
    @return: [seconds, angle1, angle2, angle3], all angles in degrees
    """
    buf = bytearray([BaroboCtx.CMD_GETMOTORANGLESTIMESTAMPABS, 0x03, 0x00])
    response = self.__transactMessage(buf)
    data = struct.unpack('<L<4f', response[2:-1])
    data[0] = data[0] / 1000.0
    data = map(rad2deg, data[1:])
    return data

  def getSerialID(self):
    """
    Get the serial ID from the Linkbot

    @return: A four character string
    """
    buf = bytearray([BaroboCtx.CMD_GETSERIALID, 3, 0])
    response = self.__transactMessage(buf) 
    botid = struct.unpack('!4s', response[2:6])[0]
    print botid
    self.serialID = botid
    return botid

  def getVersion(self):
    """
    Get the firmware version of the Linkbot
    """
    buf = bytearray([BaroboCtx.CMD_GETVERSION, 3, 0])
    response = self.__transactMessage(buf)
    return response[2]

  def isMoving(self):
    buf = bytearray([BaroboCtx.CMD_IS_MOVING, 3, 0])
    response = self.__transactMessage(buf)
    return response[2]

  def moveJoint(self, joint, angle):
    """
    Move a joint from it's current position by 'angle' degrees.

    @type joint: number
    @param joint: The joint to move: 1, 2, or 3
    @type angle: number
    @param angle: The number of degrees to move the joint from it's current
      position. For example, "45" will move the joint in the positive direction
      by 45 degrees from it's current location, and "-30" will move the joint
      in the negative direction by 30 degrees.
    """
    curangle = self.getJointAngle(joint)
    self.moveJointTo(joint, curangle + angle)

  def moveJointNB(self, joint, angle):
    """
    Non-blocking version of moveJoint(). See moveJoint() for more details.
    """
    curangle = self.getJointAngle(joint)
    self.moveJointToNB(joint, curangle + angle)

  def moveJointTo(self, joint, angle):
    """
    Move a joint to an angle.

    @type joint: number
    @param joint: The joint to move: 1, 2, or 3
    @type angle: number
    @param angle: The absolute position you want the joint to move to. Values are
      in degrees and can be any value. For example, the value "720" means two full
      rotations in the positive directions past "0".
    """
    self.moveJointToNB(joint, angle)
    self.moveWait()

  def moveJointToNB(self, joint, angle):
    """
    Non-blocking version of moveJointTo. See moveJointTo for more details.
    """
    buf = bytearray([BaroboCtx.CMD_SETMOTORANGLEABS, joint])
    buf += bytearray(struct.pack('<f', angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def move(self, angle1, angle2, angle3):
    """
    Move all of the joints on a robot by a number of degrees.

    @type angle1: number
    @param angle1: Number of degrees to move joint 1. Similar for parameters
      'angle2' and 'angle3'.
    """
    self.moveNB(angel1, angle2, angle3)
    self.moveWait()

  def moveNB(self, angle1, angle2, angle3):
    """
    Non-blocking version of move(). See move() for more details
    """
    angles = self.getJointAngles()
    self.moveToNB(angle1+angles[0], angle2+angles[1], angle3+angles[2])

  def moveTo(self, angle1, angle2, angle3):
    self.moveToNB(angle1, angle2, angle3)
    self.moveWait()

  def moveToNB(self, angle1, angle2, angle3):
    """
    Move all joints on the Linkbot. Linkbot-I modules will ignore the 'angle2'
    parameter and Linkbot-L modules will ignore the 'angle3' parmeter.

    This function is the non-blocking version of moveTo(), meaning this
    function will return immediately after the robot has begun moving and will
    not wait until the motion is finished.

    @type angle1: number
    @param angle1: Position to move the joint, in degrees
    @type angle2: number
    @param angle2: Position to move the joint, in degrees
    @type angle3: number
    @param angle3: Position to move the joint, in degrees
    """
    angle1 = deg2rad(angle1)
    angle2 = deg2rad(angle2)
    angle3 = deg2rad(angle3)
    buf = bytearray([BaroboCtx.CMD_SETMOTORANGLESABS, 0x13])
    buf += bytearray(struct.pack('<4f', angle1, angle2, angle3, 0.0))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def moveWait(self):
    """
    Wait until the current robotic motion is finished.
    """
    while self.isMoving():
      time.sleep(0.1)

  def setBuzzerFrequency(self, freq):
    """
    Set the buzzer to begin playing a tone.

    @type freq: number in Hz
    @param freq: The frequency in Hertz (Hz) for the buzzer to play. Set to
      zero to turn the buzzer off.
    """
    buf = bytearray([0x6A, 0x05, (freq>>8)&0xff, freq&0xff, 0x00])
    self.__transactMessage(buf)

  def setLEDColor(self, r, g, b):
    """
    Set the LED color

    @type r: number [0, 255]
    @type g: number [0, 255]
    @type b: number [0, 255]
    """

    buf = bytearray([BaroboCtx.CMD_RGBLED, 8, 0xff, 0xff, 0xff, r, g, b, 0x00])
    self.__transactMessage(buf)

  def smoothMoveTo(self, joint, accel0, accelf, vmax, angle):
    """
    Move a joint to a desired position with a specified amount of starting and
    stopping acceleration.

    @type joint: number
    @param joint: The joint to move
    @type accel0: number
    @param accel0: The starting acceleration, in deg/sec/sec
    @type accelf: number
    @param accelf: The stopping deceleration, in deg/sec/sec
    @type vmax: number
    @param vmax: The maximum velocity for the joint during the motion, in deg/sec
    @type angle: number
    @param angle: The absolute angle to move the joint to, in degrees
    """
    _accel0 = rad2deg(accel0)
    _accelf = rad2deg(accelf)
    _vmax = rad2deg(vmax)
    _angle = rad2deg(angle)
    buf = bytearray([BaroboCtx.CMD_SMOOTHMOVE, 20, joint])
    buf += bytearray(struct.pack('<4f', _accel0, _accelf, _vmax, _angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

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

  def twiRecv(self, addr, size):
    """
    Receive data from a TWI device. See twiSend() for more details.

    @param addr: The TWI address to send data to.
    @rtype: bytearray
    """
    twibuf = bytearray(data)
    buf = bytearray([BaroboCtx.CMD_TWI_SEND, len(data)+5, addr, len(data)])
    buf += bytearray(data)
    buf += bytearray([0x00])
    response = self.__transactMessage(buf)
    return bytearray(response[2:-1])
   
  def twiSend(self, addr, data):
    """ 
    Send data onto the Two-Wire Interface (TWI) (aka I2c) of the Linkbot.
    Many Linkbot peripherals are located on the TWI bus, including the
    accelerometer, breakout boards, and some sensors. The black phone-jack on
    top of the Linkbot exposes TWI pins where custom or prebuild peripherals
    may be attached.

    @param addr: The TWI address to send data to.
    @type data: iterable bytes
    @param data: The byte data to send to the peripheral
    """
    twibuf = bytearray(data)
    buf = bytearray([BaroboCtx.CMD_TWI_SEND, len(twibuf)+5, addr, len(twibuf)])
    buf += twibuf
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def twiSendRecv(self, addr, senddata, recvsize):
    """
    Send and receive data from a TWI device attached to the Linkbot. See
    twiSend() and twiRecv() for more details.

    @param addr: The TWI address to send data to.
    @type senddata: iterable
    @param senddata: The byte data to send to the peripheral
    @type recvsize: number
    @param recvsize: Number of bytes expected from TWI device
    @rtype: bytearray
    """
    twibuf = bytearray(senddata)
    buf = bytearray([BaroboCtx.CMD_TWI_SENDRECV, len(twibuf)+6, addr, len(twibuf)])
    buf += twibuf
    buf += bytearray([recvsize, 0x00])
    response = self.__transactMessage(buf)
    return bytearray(response[2:-1])

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

