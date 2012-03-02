import socket, re, random

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
        # Work on a copy of handlers in case one of the handlers is modifying handlers list
        for handler in self.handlers.copy():
            handler(*args, **kargs)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire

class Message:
  # For incoming messages only

  def __init__(self, line):
    line = line.rstrip('\r\n')
    pattern = '(:(?P<prefix>\S*) )?(?P<command>\S*)( (?P<params>(?P<params_no_trailing>.*?)(:(?P<trailing>.*))?))?\Z'
    m = re.match(pattern, line)
    self.groupdict = m.groupdict()
    
    self.prefix = m.group('prefix')
    self.command = m.group('command')
    self.params = m.group('params')
    self.params_no_trailing = m.group('params_no_trailing')
    self.trailing = m.group('trailing')

class Pirc:

  def __init__(self):
    self.sent = Event()
    self.received = Event()
    self.closed = Event()
    self.received += self.catch_negotiations
    self.received += self.catch_ping

  def writeline(self, s):
    # TODO: Should make an outgoing message queue that gets popped after
    # every read iteration, so as not to send a message before all handlers
    # for 'receive' have been called
    outline = s.rstrip('\r\n')
    self.sent.fire(outline)
    self.socketfile.write(outline + '\r\n')
    self.socketfile.flush()
  
  def catch_negotiations(self, msg):
    message = Message(msg)
    cmd = message.command

    if cmd == '433': #and state is negotiating connection
      self.writeline('nick {0}{1}\r\n'.format(self.attempted_nick, random.randrange(1000,9999)))
    elif cmd == '001':
      self.received -= self.catch_negotiations

  def catch_ping(self, msg):
    message = Message(msg)
    if message.command == 'PING':
      self.writeline('pong :{0}\r\n'.format(message.trailing))

  def connect(self, host, port, nick):
    self.socket = socket.create_connection((host, port))
    self.socketfile = self.socket.makefile()
    self.attempted_nick = nick

    self.writeline('user pirc 8 * :pirc\r\n') #hack
    self.writeline('nick {0}\r\n'.format(self.attempted_nick))
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

def print_outgoing_msg(msg):
  print "<<   {0}".format(msg.rstrip())

def print_incoming_msg(msg):
  print "  >> {0}".format(msg.rstrip())
  
def parse_msg(msg):
  print Message(msg).groupdict.__repr__()

def print_event(msg):
  print "!!!! {0}".format(msg.rstrip())

p = Pirc()

p.sent += (print_outgoing_msg)
p.received += (print_incoming_msg)
#p.received += (parse_msg)
p.closed += (print_event)
p.connect('irc.whatnet.org', 6667, 'pi')