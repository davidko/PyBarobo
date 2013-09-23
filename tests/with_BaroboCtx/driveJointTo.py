#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM0')
  linkbot = ctx.getLinkbot()

  linkbot.resetToZero()
  print ("Moving joint 1 90 degrees...")
  linkbot.driveJointTo(1, 0)
  time.sleep(1)
  linkbot.driveJointTo(1, 90)
  time.sleep(1)
  linkbot.driveJointTo(1, 0)
  time.sleep(1)
  print ("Moving joint 2...")
  linkbot.driveJointTo(2, 90)
  time.sleep(1)
  linkbot.driveJointTo(2, 0)
  time.sleep(1)
  print ("Moving joint 3...")
  linkbot.driveJointTo(3, 90)
  time.sleep(1)
  linkbot.driveJointTo(3, 0)
