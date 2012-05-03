from nums import Nums
from message import Message
from user import User
from event import Event
import Queue

class Channel:
  def __init__(self, connection, name):
    self.connection = connection
    self.name = name
    self.getting_names = False
    self.nicks = set()

    self.nick_added = Event()
    self.nick_removed = Event()
    self.nick_changed = Event()
    self.msg_received = Event()
    self.someone_kicked = Event() # Someone, anyone, was kicked from the channel
    self.someone_joined = Event()
    self.someone_parted = Event()
    self.someone_quit = Event()
    self.left = Event() # The pirc user is no longer in the channel

    self.connection.received += self.catch_channel_shit
    self.connection.received += self.catch_joins
    self.connection.received += self.catch_parts
    self.connection.received += self.catch_kicks
    self.connection.received += self.catch_privmsgs
    self.connection.closed += self.catch_connection_closed

    self.connection.nick_changed += self.catch_nick_changed

  def _leave(self):
    for nick in self.nicks.copy():
      self._remove_nick(nick)

  def catch_connection_closed(self, msg):
    self._leave()

  def catch_nick_changed(self, (old_nick, new_nick)):
    if old_nick in self.nicks:
      self.nicks.remove(old_nick)
      self.nicks.add(new_nick)
      self.nick_changed.fire(self, old_nick, new_nick)

  def catch_privmsgs(self, msg):
    message = Message(msg)
    if message.command == "PRIVMSG" and message.params_no_trailing[0].lower() == self.name.lower():
      user = User.parse(message.prefix)
      msg_text = message.trailing
      self.msg_received.fire(self, user, msg_text)

  def catch_kicks(self, msg):
    message = Message(msg)
    if message.command == "KICK" and message.params_no_trailing[0].lower() == self.name.lower():
      kicker = User.parse(message.prefix)
      kickee = User.parse(message.params_no_trailing[1])
      self.kicked.fire(kickee, kicker)
      self._remove_nick(kickee.nick)
      if kickee.nick == self.connection.nick:
        self._leave()

  def catch_parts(self, msg):
    message = Message(msg)
    if message.command == "PART" and message.params_no_trailing[0].lower() == self.name.lower():
      self._remove_nick(User.parse(message.prefix).nick)

  def catch_joins(self, msg):
    message = Message(msg)
    if message.command == "JOIN" and message.params_no_trailing[0].lower() == self.name.lower():
      self._add_nick(User.parse(message.prefix).nick)

  def catch_channel_shit(self, msg):
    message = Message(msg)
    if message.params_no_trailing[-1].lower() == self.name:
      if message.command == Nums.RPL_NAMREPLY:
        if not self.getting_names:
          self.getting_names = True
          self.nicks = set()
        for nick in message.trailing.split(' '):
          self._add_nick(nick.lstrip('@+%&')) # hack
      elif message.command == Nums.RPL_ENDOFNAMES:
        self.getting_names = False
        print 'synced to {0}: {1}'.format(self.name, ' '.join(self.nicks))

  def _add_nick(self, nick):
    self.nicks.add(nick)
    self.nick_added.fire(self, nick)

  def _remove_nick(self, nick):
    self.nicks.remove(nick)
    self.nick_removed.fire(self, nick)