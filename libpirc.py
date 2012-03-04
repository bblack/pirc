import socket, re, random, Queue, threading

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

class Numerics:
  RPL_TOPIC = 332

class Connection:

  def __init__(self):
    self.sent = Event()
    self.received = Event()
    self.closed = Event()
    self.received += self.catch_negotiations
    self.received += self.catch_ping

    self.event_queue = Queue.PriorityQueue()

  def writeline(self, s):
    outline = s.rstrip('\r\n')
    self.event_queue.put((0, outline))

  def _writeline(self, outline):
    # TODO: Determine if this should be after socket write/flush.
    # It would work either way. However, if the socket.write() or flush()
    # call raised an exception, the event gets fired only if it came first.
    self.sent.fire(outline)
    self.socketfile.write(outline + '\r\n')
    self.socketfile.flush()
  
  def catch_negotiations(self, msg):
    message = Message(msg)
    cmd = message.command

    if cmd == '433':
      self.writeline('NICK {0}{1}'.format(self.attempted_nick, random.randrange(1000,9999)))
    elif cmd == '001':
      self.received -= self.catch_negotiations

  def catch_ping(self, msg):
    message = Message(msg)
    if message.command == 'PING':
      self.writeline('PONG :{0}'.format(message.trailing))

  def connect(self, host, port, nick):
    self.socket = socket.create_connection((host, port))
    self.socketfile = self.socket.makefile()
    self.attempted_nick = nick

    self.writeline('USER pirc 8 * :pirc') #hack
    self.writeline('NICK {0}'.format(self.attempted_nick))

    self.read_thread = threading.Thread(target=self.read_loop_blocking)
    self.read_thread.start()

    while True:
      (pri, obj) = self.event_queue.get(True)
      if (pri, type(obj)) == (0, str):
        self._writeline(obj)
      elif (pri, type(obj)) == (1, tuple):
        event = obj[0]
        arg = obj[1]
        event.fire(arg)
      else:
        raise Exception('connect loop popped an unidentified object from the queue')
    
  def read_loop_blocking(self):
    while True:
      line = self.socketfile.readline()
      if line == '':
        self.event_queue.put((1, (self.closed, 'Received EOF from remote')))
        break
      else:
        self.event_queue.put((1, (self.received, line)))