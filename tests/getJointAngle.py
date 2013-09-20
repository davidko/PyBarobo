#!/usr/bin/env python

from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  for i in range(1,4):
    print "Joint {} angle: {}".format(i, linkbot.getJointAngle(i))
