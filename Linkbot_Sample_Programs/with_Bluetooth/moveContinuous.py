#!/usr/bin/env python

import barobo
from barobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  linkbot = Linkbot()
#linkbot.connectBluetooth('00:06:66:45:D9:F5')
  linkbot.connectBluetooth('00:06:66:4D:F6:6F')

  linkbot.resetToZero()
  print ("Moving joints forwards for 4 seconds...")
  linkbot.setJointSpeeds(-120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.resetToZero()
  linkbot.stop()
