"""Tests for escrow account balance tracking."""

import pytest
from escrow_accounting.account import EscrowAccountTracker


class TestEscrowTracker:
    def test_initial_balance(self):
        tracker = EscrowAccountTracker(initial_balance=1000.0)
        assert tracker.get_balance() == 1000.0

    def test_deposit_increases_balance(self):
        tracker = EscrowAccountTracker(500.0)
        new_bal = tracker.deposit(200.0, month=1, year=2026)
        assert new_bal == 700.0
        assert tracker.get_balance() == 700.0

    def test_disburse_decreases_balance(self):
        tracker = EscrowAccountTracker(1000.0)
        new_bal = tracker.disburse(300.0, month=6, year=2026, description="Tax")
        assert new_bal == 700.0
        assert tracker.get_balance() == 700.0

    def test_transaction_history(self):
        tracker = EscrowAccountTracker(0.0)
        tracker.deposit(500.0, 1, 2026)
        tracker.disburse(200.0, 1, 2026, "Insurance")
        txns = tracker.get_transactions()
        assert len(txns) == 2
        assert txns[0].amount == 500.0
        assert txns[1].amount == -200.0

    def test_multiple_operations(self):
        tracker = EscrowAccountTracker(1000.0)
        tracker.deposit(800.0, 1, 2026)
        tracker.disburse(3000.0, 3, 2026, "Tax installment")
        tracker.deposit(800.0, 4, 2026)
        assert tracker.get_balance() == -400.0

    def test_rounding(self):
        tracker = EscrowAccountTracker(100.0)
        tracker.deposit(33.33, 1, 2026)
        tracker.deposit(33.33, 2, 2026)
        tracker.deposit(33.34, 3, 2026)
        assert tracker.get_balance() == 200.0
