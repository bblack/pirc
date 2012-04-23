import Queue, socket, random, threading
from event import Event
from message import Message
from nums import Nums
from channel import Channel

class Connection:

  def __init__(self):
    self.sent = Event()
    self.received = Event()
    self._receiving = Event()
    self.closed = Event()
    self.received += self.catch_negotiations
    self.received += self.catch_ping
    self._receiving += self.catch_channel_shit

    self.event_queue = Queue.PriorityQueue()
    self.event_queue_ticker = 0

    self.channels = set()

  def next_event_queue_ticker(self):
    self.event_queue_ticker += 1
    return self.event_queue_ticker

  def queue_event(self, event, arg):
    self.event_queue.put((1, self.next_event_queue_ticker(), (event, arg)))

  def catch_channel_shit(self, msg):
    message = Message(msg)
    if message.command in (Nums.RPL_NAMREPLY, "JOIN"):
      self.get_or_make_channel(message.params_no_trailing[-1])

  def get_or_make_channel(self, name):
    c = None
    for i in self.channels:
      if i.name.lower() == name.lower():
        c = i
        break
    if c != None:
      return c
    else:
      c = Channel(self, name)
      self.channels.add(c)
      return c

  def writeline(self, s):
    outline = s.rstrip('\r\n')
    self.event_queue.put((0, self.next_event_queue_ticker(), outline))

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
      (pri, ticker_id, obj) = self.event_queue.get(True)
      if (pri, type(obj)) == (0, str):
        self._writeline(obj)
      elif (pri, type(obj)) == (1, tuple):
        event = obj[0]
        arg = obj[1]
        event.fire(arg)
      else:
        raise Exception('connect loop popped an unidentified object from the queue.')
    
  def read_loop_blocking(self):
    while True:
      line = self.socketfile.readline()
      if line == '':
        self.queue_event(self.closed, 'Received EOF from remote')
        break
      else:
        # The _receiving event should be used (only by self?) only
        # for setting up objects that may need to subscribe to the 'received' event
        # to catch this same incoming message. For example, if a JOIN or other channel-related
        # msg comes in for a channel not yet in the channels collection, the _receiving event
        # should create that channel, then that channel subscribes to 'received', and so it can respond
        # to this first message.
        self.queue_event(self._receiving, line)
        self.queue_event(self.received, line)