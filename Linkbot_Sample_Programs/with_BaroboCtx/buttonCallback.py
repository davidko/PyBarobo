#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time
import sys

def callback(mask, buttons, userdata):
  print ("Button press! mask: {0} buttons: {1}".format(hex(mask), hex(buttons)))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print ("Usage: {0} <Com_Port> [Linkbot Serial ID]".format(sys.argv[0]))
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None
  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot(serialID)
  linkbot.enableButtonCallback(callback)
  raw_input('Button callbacks have been enabled. Press buttons on the Linkbot. Hit Enter when done')

