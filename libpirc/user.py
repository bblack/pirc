import re

class User:
  def __init__(self, ustr):
    pattern = '(?P<nick_or_server>[^!@]*)(!(?P<user>[^@]*))?(@(?P<host>.*))?'
    m = re.match(pattern, ustr)
    
    if m.group('nick_or_server') != None:
      if '.' in m.group('nick_or_server'):
        self.nick = None
        self.server = m.group('nick_or_server')
      else:
        self.nick = m.group('nick_or_server')
        self.server = None
    self.user = m.group('user')
    self.host = m.group('host')

  @staticmethod
  def parse(ustr):
    return User(ustr)
