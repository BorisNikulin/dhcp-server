from enum import Enum, auto


class TransactionType(Enum):
    DISCOVER = auto()
    RENEW = auto()

    # from enum docs for auto labeld enums modified to use f strings
    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'


class Transaction:
    """Base class for all trnsactions."""
    transactionType: TransactionType
    transactionId: int

    def __init__(self):
        self._phase: int = 0

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.transactionId == other.transactionId
