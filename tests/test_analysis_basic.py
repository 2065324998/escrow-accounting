"""Basic analysis tests with uniform disbursements (no fiscal year issues)."""

import pytest
from escrow_accounting.models import (
    TaxAssessment,
    InsurancePolicy,
    EscrowSetup,
)
from escrow_accounting.analysis import perform_analysis


class TestAnalysisUniform:
    """Test analysis with perfectly uniform monthly disbursements.

    When all 12 months have equal disbursements, the simplified and
    aggregate methods produce the same result, so these tests pass
    regardless of the analysis method used.
    """

    def test_uniform_no_cushion_no_balance(self):
        """Uniform monthly tax, no cushion, zero balance."""
        tax = TaxAssessment(12000.0, 1, list(range(1, 13)))
        ins = InsurancePolicy(0.0, 1)
        setup = EscrowSetup(0.0, 1, 2026, tax, ins, cushion_months=0)
        result = perform_analysis(setup)
        assert result.required_monthly_deposit == 1000.0
        assert result.total_annual_disbursements == 12000.0
        assert result.shortage == 0.0
        assert result.surplus == 0.0

    def test_uniform_with_surplus(self):
        """Uniform disbursements with surplus should refund over 12 months."""
        tax = TaxAssessment(12000.0, 1, list(range(1, 13)))
        ins = InsurancePolicy(0.0, 1)
        setup = EscrowSetup(500.0, 1, 2026, tax, ins, cushion_months=0)
        result = perform_analysis(setup)
        assert result.surplus == 500.0
        expected = round(1000.0 - 500.0 / 12, 2)
        assert result.required_monthly_deposit == expected

    def test_projections_length(self):
        """Analysis should produce 12 monthly projections."""
        tax = TaxAssessment(12000.0, 1, list(range(1, 13)))
        ins = InsurancePolicy(0.0, 1)
        setup = EscrowSetup(0.0, 1, 2026, tax, ins, cushion_months=0)
        result = perform_analysis(setup)
        assert len(result.projections) == 12
