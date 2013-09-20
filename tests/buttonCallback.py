#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time

def callback(mask, buttons, userdata):
  print "Button press! mask: {} buttons: {}".format(hex(mask), hex(buttons))

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()
  linkbot.enableButtonCallback(callback)
  raw_input('Button callbacks have been enabled. Press buttons on the Linkbot. Hit Enter when done')

