#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  # Set all pins to input
  map( lambda pin: linkbot.setBreakoutPinMode(pin, barobo.PINMODE_INPUT), range(2,14))

  print map(linkbot.getBreakoutDigitalPin, range(2, 14))
