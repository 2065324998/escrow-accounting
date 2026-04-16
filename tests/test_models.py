"""Tests for escrow accounting data models."""

import pytest
from datetime import date
from escrow_accounting.models import (
    TaxAssessment,
    TaxRateChange,
    InsurancePolicy,
    EscrowSetup,
    ProjectionMonth,
    AnalysisResult,
)


class TestTaxAssessment:
    def test_creation(self):
        tax = TaxAssessment(
            annual_amount=6000.0,
            fiscal_year_start_month=7,
            installment_months=[3, 9],
        )
        assert tax.annual_amount == 6000.0
        assert tax.fiscal_year_start_month == 7
        assert tax.installment_months == [3, 9]

    def test_per_installment_semi_annual(self):
        tax = TaxAssessment(6000.0, 7, [3, 9])
        assert tax.per_installment() == 3000.0

    def test_per_installment_quarterly(self):
        tax = TaxAssessment(8000.0, 1, [3, 6, 9, 12])
        assert tax.per_installment() == 2000.0

    def test_per_installment_annual(self):
        tax = TaxAssessment(5000.0, 1, [12])
        assert tax.per_installment() == 5000.0


class TestTaxRateChange:
    def test_creation(self):
        change = TaxRateChange(
            new_annual_amount=6600.0,
            effective_fiscal_year_start=date(2026, 7, 1),
        )
        assert change.new_annual_amount == 6600.0
        assert change.effective_fiscal_year_start == date(2026, 7, 1)


class TestInsurancePolicy:
    def test_creation(self):
        policy = InsurancePolicy(annual_premium=1800.0, renewal_month=6)
        assert policy.annual_premium == 1800.0
        assert policy.renewal_month == 6


class TestEscrowSetup:
    def test_defaults(self):
        tax = TaxAssessment(6000.0, 1, [6, 12])
        ins = InsurancePolicy(1800.0, 9)
        setup = EscrowSetup(
            current_balance=1000.0,
            analysis_month=1,
            analysis_year=2026,
            tax=tax,
            insurance=ins,
        )
        assert setup.cushion_months == 2
        assert setup.anticipated_tax_changes == []
        assert setup.anticipated_insurance_premium is None

    def test_custom_cushion(self):
        tax = TaxAssessment(6000.0, 1, [6, 12])
        ins = InsurancePolicy(1800.0, 9)
        setup = EscrowSetup(500.0, 1, 2026, tax, ins, cushion_months=1)
        assert setup.cushion_months == 1

    def test_with_anticipated_changes(self):
        tax = TaxAssessment(6000.0, 7, [3, 9])
        ins = InsurancePolicy(1800.0, 6)
        changes = [TaxRateChange(6600.0, date(2026, 7, 1))]
        setup = EscrowSetup(
            current_balance=1200.0,
            analysis_month=1,
            analysis_year=2026,
            tax=tax,
            insurance=ins,
            anticipated_tax_changes=changes,
            anticipated_insurance_premium=1900.0,
        )
        assert len(setup.anticipated_tax_changes) == 1
        assert setup.anticipated_insurance_premium == 1900.0


class TestProjectionMonth:
    def test_total_disbursement(self):
        pm = ProjectionMonth(
            month=6,
            year=2026,
            deposit=800.0,
            tax_disbursement=3000.0,
            insurance_disbursement=1800.0,
            ending_balance=500.0,
        )
        assert pm.total_disbursement == 4800.0

    def test_zero_disbursements(self):
        pm = ProjectionMonth(
            month=1, year=2026, deposit=800.0,
            tax_disbursement=0.0, insurance_disbursement=0.0,
            ending_balance=1800.0,
        )
        assert pm.total_disbursement == 0.0


class TestAnalysisResult:
    def test_creation(self):
        result = AnalysisResult(
            required_monthly_deposit=856.25,
            total_annual_disbursements=8100.0,
            cushion_amount=1350.0,
            shortage=2175.0,
            surplus=0.0,
            projections=[],
        )
        assert result.required_monthly_deposit == 856.25
        assert result.shortage == 2175.0
        assert result.surplus == 0.0
