#!/usr/bin/env python

from barobo import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connectBluetooth('00:06:66:4D:F6:6F')

  linkbot.resetToZero()
  print ("Moving joints to 90 degrees...")
  linkbot.driveTo(90, 90, 90)
  time.sleep(1)
  print ("Moving joints to 0 degrees...")
  linkbot.driveTo(0, 0, 0)
