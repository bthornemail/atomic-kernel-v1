// braces and parens in comments should not count: { } ( )
export const left = "{";
export const right = ")";
export function buildMessage(name: string) {
  const msg = `hello ${name}, symbols: { ) }`;
  return msg + " /* not a comment */ ";
}
