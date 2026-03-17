import subsystem_a
import subsystem_b

class ServiceFacade:
  def run(self):
    return subsystem_a.start()

  def stop(self):
    return subsystem_b.stop()
