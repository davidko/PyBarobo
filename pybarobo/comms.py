#!/usr/bin/env python

import socket
import serial
import threading

class Packet:
  def __init__(self, data=None, addr=None):
    self.data = data
    self.addr = addr

  def __getitem__(self, key):
    return self.data[key]

class PhysicalLayer_TTY(serial.Serial):
  def __init__(self, ttyfilename):
    serial.Serial.__init__(self, ttyfilename, baudrate=230400)
    self.timeout = None

class PhysicalLayer_Socket(socket.socket):
  def __init__(self, hostname, port):
    socket.socket.__init__(self)
    self.connect((hostname, port))

  def flush(self):
    pass
  def flushInput(self):
    pass
  def flushOutput(self):
    pass

  def read(self):
    # Read and return a single byte
    return self.recv(1)

  def write(self, packet):
    self.sendall(packet)

class LinkLayer_Base:
  def __init__(self, physicalLayer, readCallback):
    self.phys = physicalLayer
    self.deliver = readCallback
    self.writeLock = threading.Lock()

  def start(self):
    self.thread = threading.Thread(target=self._run)
    self.thread.daemon = True
    self.thread.start()

class LinkLayer_TTY(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    newpacket = bytearray([ packet[0],
                            len(packet)+5,
                            address>>8,
                            address&0x00ff,
                            1 ])
    newpacket += bytearray(packet)
    self.writeLock.acquire()
    #print "Send: {}".format(map(hex, newpacket))
    self.phys.write(newpacket)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        print "Recv: {}".format(map(hex, self.readbuf))
        zigbeeAddr = struct.unpack('!H', self.readbuf[2:4])[0]
        if self.readbuf[0] != BaroboCtx.EVENT_REPORTADDRESS:
          pkt = Packet(self.readbuf[5:-1], zigbeeAddr)
        else:
          pkt = Packet(self.readbuf, zigbeeAddr)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]

class LinkLayer_Socket(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    self.writeLock.acquire()
    print "Send: {}".format(map(hex, packet))
    self.phys.write(packet)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        print "Recv: {}".format(map(hex, self.readbuf))
        pkt = Packet(self.readbuf, 0x8000)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]


