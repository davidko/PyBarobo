#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: {0} <Com_Port>".format(sys.argv[0])
    quit()
  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot()

  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(880);
  time.sleep(1)
  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(0);
