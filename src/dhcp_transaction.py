from enum import Enum, auto

class TransactionType(Enum):
    RENEW = auto()
    RELEASE = auto()

    # from enum docs for auto labeld enums modified to use f strings
    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'

class Transaction:
    transactionType: TransactionType

    def __init__(self):
        self._phase: int = 0
        self.transactionId: int
