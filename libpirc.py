import socket

class Event:
    # Copied from http://www.valuedlessons.com/2008/04/events-in-python.html
    # and modified
  
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire

class Pirc:

  def __init__(self):
    self.received = Event()
    self.closed = Event()
    
  def connect(self, host, port):
    self.socket = socket.create_connection((host, port))
    self.socketfile = self.socket.makefile()
    while True:
      line = self.socketfile.readline()
      if line == '':
        self.closed.fire('Received EOF from remote')
        break
      else:
        self.received.fire(line)

#
# All below this line is for debugging
#

def print_incoming_line(line):
  print "  >>{0}".format(line.rstrip())
  
def print_event(msg):
  print "!!!! {0}".format(msg.rstrip())

p = Pirc()
p.received += (print_incoming_line)
p.closed += (print_event)
p.connect('irc.whatnet.org', 6667)