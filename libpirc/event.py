class Event:
  # Copied from http://www.valuedlessons.com/2008/04/events-in-python.html
  # and modified
  
  def __init__(self):
    self.handlers = []

  def handle(self, handler):
    if handler not in self.handlers:
      self.handlers.append(handler)
    return self

  def unhandle(self, handler):
    try:
      self.handlers.remove(handler)
    except:
      raise ValueError("Handler is not handling this event, so cannot unhandle it.")
    return self

  def fire(self, *args, **kargs):
    # Work on a copy of handlers in case one of the handlers is modifying handlers list
    for handler in self.handlers[:]:
      handler(*args, **kargs)

  __iadd__ = handle
  __isub__ = unhandle
  __call__ = fire