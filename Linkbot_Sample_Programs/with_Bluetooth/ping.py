#!/usr/bin/env python

from barobo.linkbot import Linkbot
import time
import sys
import numpy
import pylab

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connectBluetooth('00:06:66:4D:F6:6F')
  numerrors = 0
  numtries = 500
  pingsum = 0
  pings = []
  linkbot.ping()
  for _ in range(numtries):
    try:
      ping = linkbot.ping(32)
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

  pylab.hist(pings)
  pylab.show()

