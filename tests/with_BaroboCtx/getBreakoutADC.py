#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  adcs = map(linkbot.getBreakoutADC, range(0,8))
  print map(lambda x: x/1024.0*5.0, adcs)
