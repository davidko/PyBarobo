#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import math
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

  # Set pin to output
  pin = 11
  linkbot.setBreakoutPinMode(pin, barobo.PINMODE_OUTPUT)
  t = 0.0
  for i in range (0, 500):
    linkbot.setBreakoutAnalogPin(pin, int(127*math.sin(t*3))+127)
    time.sleep(0.01)
    t += 0.01

