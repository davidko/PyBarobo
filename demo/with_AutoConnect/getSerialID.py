#!/usr/bin/env python

from barobo import Linkbot, Dongle
import time
import sys

if __name__ == "__main__":
    dongle = Dongle()
    dongle.connect()
    linkbot = dongle.getLinkbot()

    print (linkbot.getSerialID())
