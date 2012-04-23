#!/usr/bin/python
# For debugging

import threading, sys
from libpirc.connection import Connection

def print_outgoing_msg(msg):
  print "<<   {0}".format(msg.rstrip())

def print_incoming_msg(msg):
  print "  >> {0}".format(msg.rstrip())
  
def parse_msg(msg):
  print Message(msg).groupdict.__repr__()

def print_event(msg):
  print "!!!! {0}".format(msg.rstrip())

p = Connection()

p.sent += (print_outgoing_msg)
p.received += (print_incoming_msg)
#p.received += (parse_msg)
p.closed += (print_event)
t = threading.Thread(target=p.connect, args = ('irc.whatnet.org', 6667, 'pi'))
t.start()

while True:
  try:
    cmd = sys.stdin.readline()
    p.writeline(cmd)
  except KeyboardInterrupt:
    print '' #since some terms show ^C on interrupt
    print 'got interrupt, quitting forcefully'
    exit()