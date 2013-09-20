#!/usr/bin/env python

from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot('BNQD')
  print linkbot
  print linkbot.getVersion()
  linkbot.recordAnglesBegin()
  s = raw_input('Press enter to continue...')
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
  for i in range(1,4):
    linkbot.setJointSpeed(i, 120)
  while True:
    linkbot.moveToNB(360, 0, -360)
    linkbot.moveWait()
    linkbot.moveToNB(0, 0, 0)
    linkbot.moveWait()
