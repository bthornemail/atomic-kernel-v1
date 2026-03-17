class PaymentAdapter(Entity):
  def pay(self, amount):
    return gateway.process(amount)
