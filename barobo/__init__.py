#!/usr/bin/env python

"""
The Barobo Python Module

This python module can be used to control Barobo robots. The easiest way to use
this package is in conjunction with BaroboLink. After connecting to the robots
you want to control in BaroboLink, the following python program will move
joints 1 and 3 on the first connected Linkbot in BaroboLink::

  from pybarobo import Linkbot
  linkbot = Linkbot()
  linkbot.connect()
  linkbot.moveTo(180, 0, -180)

You may also use this package to control Linkbots without BaroboLink. In that
case, a typical control program will look something like this::
  from pybarobo import Linkbot, BaroboCtx

  ctx = BaroboCtx()
  ctx.connectDongleTTY('COM3')
  linkbot = ctx.getLinkbot() # or linkbot = ctx.getLinkbot('2B2C')
  linkbot.moveTo(180, 0, -180)

For more documentation, please refer to the documentation under the
pybarobo.linkbot module.
"""

from linkbot import *
from barobo import *

