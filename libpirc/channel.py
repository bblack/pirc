from nums import Nums
from message import Message
from user import User
from event import Event

class Channel:
  def __init__(self, connection, name):
    self.connection = connection
    self.name = name
    self.getting_names = False
    self.nicks = set()

    self.nick_added = Event()
    self.nick_removed = Event()

    self.connection.received += self.catch_channel_shit
    self.connection.received += self.catch_joins
    self.connection.received += self.catch_parts
    self.connection.received += self.catch_kicks

  def catch_kicks(self, msg):
    message = Message(msg)
    if message.command == "KICK" and message.params_no_trailing[0].lower() == self.name.lower():
      self._remove_nick(User.parse(message.params_no_trailing[1]).nick)
      # TODO: Handle case where kickee is me

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
    self.nick_added.fire(nick)

  def _remove_nick(self, nick):
    self.nicks.remove(nick)
    self.nick_removed.fire(nick)