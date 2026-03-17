import subsystem_a
import subsystem_b

class ServiceFacade:
  def run(self):
    return subsystem_a.start()

  def stop(self):
    return subsystem_b.stop()

class ReportBuilder:
  def with_title(self, title):
    return title

  def build(self):
    return renderer.build()
