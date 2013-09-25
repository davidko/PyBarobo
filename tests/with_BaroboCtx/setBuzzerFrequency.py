#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import barobo
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(880);
  time.sleep(1)
  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(0);
