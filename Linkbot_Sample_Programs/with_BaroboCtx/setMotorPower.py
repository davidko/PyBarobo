#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Usage: {0} <Com_Port> [Linkbot Serial ID]".format(sys.argv[0])
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None

  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot(serialID)

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
