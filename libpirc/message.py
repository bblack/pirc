import re

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
    self.params_no_trailing = m.group('params_no_trailing').strip().split(' ')
    self.trailing = m.group('trailing')
