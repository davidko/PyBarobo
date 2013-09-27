#!/usr/bin/env python

from barobo.linkbot import Linkbot
from barobo import BaroboCtx
import time
import sys
import numpy

if __name__ == "__main__":
  import pdb
  pdb.set_trace()
  ctx = BaroboCtx()
  ctx.connectDongleTTY('/dev/ttyACM1')
#linkbot = ctx.getLinkbot('WWMG')
  linkbot = ctx.getLinkbot('LGFP')
  numerrors = 0
  numtries = 500
  pingsum = 0
  pings = []
  linkbot.ping()
  for _ in range(numtries):
    try:
      ping = linkbot.ping()
      pings.append(ping)
      sys.stdout.write('.')
      sys.stdout.flush()
    except:
      numerrors += 1
      sys.stdout.write('x')
      sys.stdout.flush()

  sys.stdout.write('\n')
  print("{} tries, {} errors".format(numtries, numerrors))

  print("{} errors, avg ping: {}, stddev: {}".format(numerrors, numpy.mean(pings), numpy.std(pings)))

