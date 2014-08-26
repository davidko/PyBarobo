#!/usr/bin/env python

from barobo import Linkbot, Dongle
import barobo
import math
import time
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} [Linkbot Serial ID]".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    dongle = Dongle()
    dongle.connect()
    linkbot = dongle.getLinkbot(serialID)

    # Set pin to output
    pin = 11
    linkbot.setBreakoutPinMode(pin, barobo.PINMODE_OUTPUT)
    t = 0.0
    for i in range (0, 500):
        linkbot.setBreakoutAnalogPin(pin, int(127*math.sin(t*3))+127)
        time.sleep(0.01)
        t += 0.01

