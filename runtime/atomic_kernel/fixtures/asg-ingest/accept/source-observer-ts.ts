class Subject {
  notify() {
    this.emit("changed");
  }
}

export function watch(subject: Subject) {
  subject.notify();
}
