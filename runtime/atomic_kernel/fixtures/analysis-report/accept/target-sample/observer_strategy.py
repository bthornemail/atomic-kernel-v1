class Subject:
  def register(self, listener):
    return listener

  def notify(self, listener):
    return listener.update()

class Context:
  def run(self):
    return self.strategy.execute()
