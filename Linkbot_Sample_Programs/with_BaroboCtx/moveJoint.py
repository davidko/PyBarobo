#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Usage: {0} <Com_Port>".format(sys.argv[0])
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None
  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot(serialID)

  linkbot.resetToZero()
  print ("Moving joint 1 90 degrees...")
  linkbot.moveJoint(1, 90)
  time.sleep(1)
  print ("Moving joint 2...")
  linkbot.moveJoint(2, 90)
  time.sleep(1)
  print ("Moving joint 3...")
  linkbot.moveJoint(3, 90)
  time.sleep(1)
