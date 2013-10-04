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
  print (linkbot)
  print (linkbot.getVersion())
  linkbot.recordAnglesBegin()
  s = raw_input('Press enter to continue...')
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
  for i in range(1,4):
    linkbot.setJointSpeed(i, 120)
  linkbot.moveToNB(360, 0, -360)
  linkbot.moveWait()
  linkbot.moveToNB(0, 0, 0)
  linkbot.moveWait()
