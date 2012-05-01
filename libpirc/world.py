from event import Event
from connection import Connection

class World:

  def __init__(self):
    self.connections = []
    self.connection_added = Event()

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
    self.connection_added.fire(self, conn)
    return conn

  def shut_it_down(self):
    for c in self.connections:
      c.shut_it_down()
