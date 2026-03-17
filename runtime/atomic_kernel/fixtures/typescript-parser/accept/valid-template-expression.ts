export function render(user: { name: string; age: number }) {
  const detail = `${user.name} -> ${(() => ({ age: user.age }))().age}`;
  return detail;
}
