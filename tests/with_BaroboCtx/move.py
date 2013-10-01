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
  print ("Moving all joints 90 degrees...")
  linkbot.move(90, 90, 90)
