import { floor } from "mathx";

class Account extends Entity {
  deposit(amount: number) {
    return floor(amount);
  }
}

export function makeAccount(x: number) {
  return new Account();
}
