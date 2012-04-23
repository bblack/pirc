from nums import Nums
from message import Message

class Channel:
  def __init__(self, connection, name):
    self.connection = connection
    self.name = name
    self.getting_names = False
    self.nicks = set()

    self.connection.received += self.catch_channel_shit

  def catch_channel_shit(self, msg):
    message = Message(msg)
    if message.params_no_trailing[-1].lower() == self.name:
      if message.command == Nums.RPL_NAMREPLY:
        if not self.getting_names:
          self.getting_names = True
          self.nicks = set()
        for nick in message.trailing.split(' '):
          self.nicks.add(nick)
      elif message.command == Nums.RPL_ENDOFNAMES:
        self.getting_names = False
        print 'synced to {0}: {1}'.format(self.name, ' '.join(self.nicks))