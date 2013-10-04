#!/usr/bin/env python

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
  linkbot.stop()
  linkbot.setMotorPowers(-255, -255, -255)
  time.sleep(5)
  print linkbot.getJointAngles()
  linkbot.resetToZero()
  linkbot.stop()
  linkbot.setMotorPowers(255, 255, 255)
  time.sleep(5)
  print linkbot.getJointAngles()
  linkbot.stop()
