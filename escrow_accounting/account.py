"""Escrow account balance tracking."""

from dataclasses import dataclass, field


@dataclass
class Transaction:
    """A single escrow account transaction."""

    month: int
    year: int
    description: str
    amount: float
    balance_after: float


class EscrowAccountTracker:
    """Track escrow account balance and transactions."""

    def __init__(self, initial_balance: float):
        self.balance = initial_balance
        self.transactions: list[Transaction] = []

    def deposit(
        self,
        amount: float,
        month: int,
        year: int,
        description: str = "Monthly deposit",
    ) -> float:
        """Record a deposit and return new balance."""
        self.balance = round(self.balance + amount, 2)
        self.transactions.append(
            Transaction(
                month=month,
                year=year,
                description=description,
                amount=amount,
                balance_after=self.balance,
            )
        )
        return self.balance

    def disburse(
        self,
        amount: float,
        month: int,
        year: int,
        description: str = "Disbursement",
    ) -> float:
        """Record a disbursement and return new balance."""
        self.balance = round(self.balance - amount, 2)
        self.transactions.append(
            Transaction(
                month=month,
                year=year,
                description=description,
                amount=-amount,
                balance_after=self.balance,
            )
        )
        return self.balance

    def get_balance(self) -> float:
        """Return current balance."""
        return self.balance

    def get_transactions(self) -> list[Transaction]:
        """Return transaction history."""
        return list(self.transactions)
