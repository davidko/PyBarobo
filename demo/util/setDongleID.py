#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time
import sys
import random

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ("Usage: {0} <Com_Port> ".format(sys.argv[0]))
        quit()
    ctx = BaroboCtx()
    ctx.connectDongleSFP(sys.argv[1])
    linkbot = ctx.getLinkbot()
    new_id = bytearray([random.randint(0, 255) for _ in range(4)])
    new_id[1] |= 0x80
    linkbot._setSerialID(new_id)
    print('Set dongle id to: ')
    print(map(hex, new_id))
