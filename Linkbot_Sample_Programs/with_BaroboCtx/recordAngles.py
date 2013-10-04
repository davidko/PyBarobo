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
  linkbot.recordAnglesBegin(delay=0.1)
  linkbot.smoothMoveTo(1, 100, 100, 100, 360)
  linkbot.smoothMoveTo(2, 100, 100, 100, 360)
  linkbot.smoothMoveTo(3, 100, 100, 100, 360)
  linkbot.moveWait()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
