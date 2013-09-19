#!/usr/bin/env python

import serial
import time
import array
import Queue
import threading
import struct
import math
import socket

from pybarobo.linkbot import Linkbot

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
