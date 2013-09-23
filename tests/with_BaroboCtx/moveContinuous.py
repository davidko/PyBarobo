#!/usr/bin/env python

import barobo
from barobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print ("Moving joints forwards for 4 seconds...")
  linkbot.setJointSpeeds(120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.stop()
