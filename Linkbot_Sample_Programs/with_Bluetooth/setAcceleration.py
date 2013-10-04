#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connectBluetooth('00:06:66:45:D9:F5')

  linkbot.setAcceleration(240)
  linkbot.recordAnglesBegin()
  for _ in range(3):
    linkbot.setJointStates(
        [barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_BACKWARD], 
        [120, 120, 120])
    time.sleep(2)
    linkbot.setJointStates(
        [barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD, barobo.ROBOT_FORWARD], 
        [120, 120, 120])
    time.sleep(2)
  linkbot.stop()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
