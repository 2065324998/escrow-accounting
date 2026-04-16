"""Tests for insurance disbursement calculations."""

import pytest
from escrow_accounting.insurance import compute_monthly_insurance_disbursements
from escrow_accounting.models import InsurancePolicy


class TestInsuranceDisbursements:
    def test_renewal_month_amount(self):
        policy = InsurancePolicy(annual_premium=1800.0, renewal_month=6)
        result = compute_monthly_insurance_disbursements(policy, 1, 2026)
        amounts = {r[0]: r[2] for r in result}
        assert amounts[6] == 1800.0

    def test_non_renewal_months_zero(self):
        policy = InsurancePolicy(annual_premium=1800.0, renewal_month=6)
        result = compute_monthly_insurance_disbursements(policy, 1, 2026)
        for month_num, year, amount in result:
            if month_num != 6:
                assert amount == 0.0

    def test_anticipated_premium(self):
        policy = InsurancePolicy(annual_premium=1800.0, renewal_month=6)
        result = compute_monthly_insurance_disbursements(
            policy, 1, 2026, anticipated_premium=2000.0
        )
        amounts = {r[0]: r[2] for r in result}
        assert amounts[6] == 2000.0

    def test_twelve_months_generated(self):
        policy = InsurancePolicy(annual_premium=1800.0, renewal_month=6)
        result = compute_monthly_insurance_disbursements(policy, 1, 2026)
        assert len(result) == 12

    def test_mid_year_start_wraps(self):
        """Analysis starting July should wrap months correctly."""
        policy = InsurancePolicy(annual_premium=1200.0, renewal_month=3)
        result = compute_monthly_insurance_disbursements(policy, 7, 2026)
        months = [r[0] for r in result]
        assert months == [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
        amounts = {r[0]: r[2] for r in result}
        assert amounts[3] == 1200.0

    def test_zero_premium(self):
        """Zero premium produces zero disbursements everywhere."""
        policy = InsurancePolicy(annual_premium=0.0, renewal_month=9)
        result = compute_monthly_insurance_disbursements(policy, 1, 2026)
        assert all(r[2] == 0.0 for r in result)
