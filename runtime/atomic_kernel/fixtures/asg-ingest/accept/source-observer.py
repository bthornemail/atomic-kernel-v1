class Subject:
  def notify(self):
    self.emit("changed")


def watch(subject):
  subject.notify()
