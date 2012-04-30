from event import Event
from connection import Connection

class World:

  def __init__(self):
    self.connections = []

  def make_new_connection(self):
    conn = Connection()
    self.connections += conn
    return conn
