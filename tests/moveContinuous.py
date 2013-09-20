#!/usr/bin/env python

import pybarobo
from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print "Moving joints forwards for 4 seconds..."
  linkbot.setJointSpeeds(90, 90, 90)
  linkbot.moveContinuous(pybarobo.ROBOT_FORWARD, pybarobo.ROBOT_FORWARD, pybarobo.ROBOT_FORWARD)
  time.sleep(4)
  linkbot.stop()
