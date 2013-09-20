#!/usr/bin/env python

from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print "Moving joint 1 90 degrees..."
  linkbot.moveJoint(1, 90)
  time.sleep(1)
  print "Moving joint 2..."
  linkbot.moveJoint(2, 90)
  time.sleep(1)
  print "Moving joint 3..."
  linkbot.moveJoint(3, 90)
  time.sleep(1)
