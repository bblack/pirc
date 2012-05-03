from event import Event
from connection import Connection

class World:

  def __init__(self):
    self.connections = []
    self.connection_added = Event()
    self.channel_opened = Event()

  def get_connections(self):
    ret = []
    for c in self.connections:
      ret.append(c)
    return ret

  def remove_connection(self, connection):
    if connection.is_connected:
      raise "I don't think so, tim"
    self.connections.remove(connection)

  def new_connection(self):
    conn = Connection()
    self.connections.append(conn)

    conn.channel_opened += self.handle_channel_opened

    self.connection_added.fire(self, conn)
    return conn

  def shut_it_down(self):
    for c in self.connections:
      c.shut_it_down()

  def handle_channel_opened(self, channel):
    self.channel_opened.fire(self, channel)