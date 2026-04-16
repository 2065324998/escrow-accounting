"""Tests for tax proration with calendar-year fiscal year (no boundary issues)."""

import pytest
from escrow_accounting.tax_proration import compute_monthly_tax_disbursements
from escrow_accounting.models import TaxAssessment


class TestCalendarYearTax:
    """Tax proration tests using January fiscal year start (calendar year).

    These tests verify basic tax disbursement calculations where the fiscal
    year aligns with the calendar year, so fiscal year boundary logic
    is not exercised.
    """

    def test_semi_annual_amounts(self):
        tax = TaxAssessment(
            annual_amount=6000.0,
            fiscal_year_start_month=1,
            installment_months=[6, 12],
        )
        result = compute_monthly_tax_disbursements(tax, 1, 2026, [])
        installments = [r[2] for r in result if r[2] > 0]
        assert installments == [3000.0, 3000.0]

    def test_quarterly_amounts(self):
        tax = TaxAssessment(
            annual_amount=8000.0,
            fiscal_year_start_month=1,
            installment_months=[3, 6, 9, 12],
        )
        result = compute_monthly_tax_disbursements(tax, 1, 2026, [])
        installments = [r[2] for r in result if r[2] > 0]
        assert len(installments) == 4
        assert all(a == 2000.0 for a in installments)

    def test_non_installment_months_zero(self):
        tax = TaxAssessment(6000.0, 1, [6, 12])
        result = compute_monthly_tax_disbursements(tax, 1, 2026, [])
        for month_num, year, amount in result:
            if month_num not in [6, 12]:
                assert amount == 0.0, f"Month {month_num} should be 0"

    def test_twelve_months_generated(self):
        tax = TaxAssessment(6000.0, 1, [6, 12])
        result = compute_monthly_tax_disbursements(tax, 1, 2026, [])
        assert len(result) == 12

    def test_total_matches_annual(self):
        tax = TaxAssessment(6000.0, 1, [6, 12])
        result = compute_monthly_tax_disbursements(tax, 1, 2026, [])
        total = sum(r[2] for r in result)
        assert total == 6000.0

    def test_mid_year_analysis_start(self):
        """Analysis starting in July should wrap months correctly."""
        tax = TaxAssessment(6000.0, 1, [6, 12])
        result = compute_monthly_tax_disbursements(tax, 7, 2026, [])
        months = [r[0] for r in result]
        assert months == [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
        total = sum(r[2] for r in result)
        assert total == 6000.0

    def test_month_year_tuples(self):
        """Verify month/year values in returned tuples."""
        tax = TaxAssessment(6000.0, 1, [6, 12])
        result = compute_monthly_tax_disbursements(tax, 11, 2025, [])
        assert result[0][:2] == (11, 2025)
        assert result[1][:2] == (12, 2025)
        assert result[2][:2] == (1, 2026)
        assert result[11][:2] == (10, 2026)
