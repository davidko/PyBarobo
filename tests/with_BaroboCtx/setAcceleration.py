#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.setAcceleration(240)
  while True:
    linkbot.setJointStates(
        [barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD], 
        [120, 120, 120])
    time.sleep(2)
    linkbot.setJointStates(
        [barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD], 
        [120, 120, 120])
    time.sleep(2)
