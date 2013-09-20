#!/usr/bin/env python

from pybarobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()
  linkbot.resetToZero()
  linkbot.recordAnglesBegin(delay=0.1)
  linkbot.smoothMoveTo(1, 100, 100, 100, 360)
  linkbot.smoothMoveTo(2, 100, 100, 100, 360)
  linkbot.smoothMoveTo(3, 100, 100, 100, 360)
  linkbot.moveWait()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
