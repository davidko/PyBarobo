#!/usr/bin/env python

import barobo
from barobo import Linkbot, BaroboCtx
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: {0} <Com_Port>".format(sys.argv[0])
    quit()
  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print ("Moving joints forwards for 4 seconds...")
  linkbot.setJointSpeeds(120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.resetToZero()
  linkbot.stop()
