#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import math
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  # Set pin to output
  pin = 11
  linkbot.setBreakoutPinMode(pin, barobo.PINMODE_OUTPUT)
  t = 0.0
  for i in range (0, 500):
    linkbot.setBreakoutAnalogPin(pin, int(127*math.sin(t*3))+127)
    time.sleep(0.01)
    t += 0.01

