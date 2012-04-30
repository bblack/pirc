#!/usr/bin/python
# For debugging

import threading, sys
from libpirc.connection import Connection

class Test:
  def print_outgoing_msg(self, msg):
    print "<<   {0}".format(msg.rstrip())

  def print_incoming_msg(self, msg):
    print "  >> {0}".format(msg.rstrip())
    
  def parse_msg(self, msg):
    print Message(msg).groupdict.__repr__()

  def print_event(self, msg):
    print "!!!! {0}".format(msg.rstrip())

  def chan_msg_rcvd(self, (channel, user, msg_text)):
    print "{0}: <{1}> {2}".format(channel.name, user.nick, msg_text)

  def __init__(self, connection):
    self.connection = connection
    p = connection
    p.sent += self.print_outgoing_msg
    p.received += self.print_incoming_msg
    #p.received += self.parse_msg
    p.closed += self.print_event
    p.channel_msg_received += self.chan_msg_rcvd
    t = threading.Thread(target=self.test_loop)
    t.start()

  def test_loop(self):
    p = self.connection
    while True:
      try:
        cmd = sys.stdin.readline()
        if cmd.strip() == 'nicks':
          for chan in p.channels:
            print chan.name + ' -- ' + ','.join(chan.nicks)
        else:
          p.writeline(cmd)
      except KeyboardInterrupt:
        print '' #since some terms show ^C on interrupt
        print 'got interrupt, quitting forcefully'
        exit()