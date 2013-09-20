#!/usr/bin/env python

from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print "Moving joints to 90 degrees..."
  linkbot.driveTo(90, 90, 90)
  time.sleep(1)
  print "Moving joints to 0 degrees..."
  linkbot.driveTo(0, 0, 0)
