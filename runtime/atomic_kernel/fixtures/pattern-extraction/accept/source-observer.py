class Subject:
  def register(self, listener):
    return listener

  def notify(self, listener):
    return listener.update()
