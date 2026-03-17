class Subject {
  register(listener) {
    return listener;
  }
  notify(listener) {
    return listener.update();
  }
}

class Context {
  run() {
    return this.strategy.execute();
  }
}
