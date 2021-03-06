#!/usr/bin/env python

from barobo import Linkbot, Dongle
import barobo
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

    linkbot.setAcceleration(240)
    for _ in range(3):
        linkbot.setJointStates(
                [barobo.ROBOT_FORWARD, 
                 barobo.ROBOT_FORWARD, 
                 barobo.ROBOT_BACKWARD], 
                [120, 120, 120])
        time.sleep(2)
        linkbot.setJointStates(
                [barobo.ROBOT_BACKWARD, 
                 barobo.ROBOT_BACKWARD, 
                 barobo.ROBOT_FORWARD], 
                [120, 120, 120])
        time.sleep(2)
    linkbot.stop()
