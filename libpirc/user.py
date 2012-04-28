class User:
  def __init__(self, ustr):
    #HACK
    self.nick = ustr.split('!', 1)[0]

  @staticmethod
  def parse(ustr):
    return User(ustr)
