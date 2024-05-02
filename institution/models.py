class Transaction():
    def __init__(self, date, description, amount):
        self.date = date
        self.description = description
        self.amount = amount

    def __hash__(self):
        return hash((self.description,
                     self.amount, 
                     self.date))
    
    def __eq__(self, other):
        return isinstance(other, Transaction) and \
               self.date == other.date and \
               self.description == other.description and \
               self.amount == other.amount

    def __repr__(self):
        return (f"({self.amount}, "
                f"{self.date}, "
                f"{self.description})")

