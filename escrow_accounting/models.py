"""Data models for escrow accounting."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class TaxAssessment:
    """Property tax assessment details.

    Properties:
        annual_amount: Current annual tax amount
        fiscal_year_start_month: Month when the tax fiscal year begins (1-12)
            e.g., 7 for July (common for many US jurisdictions)
        installment_months: Months when tax installments are due
            e.g., [3, 9] for March and September semi-annual payments
    """

    annual_amount: float
    fiscal_year_start_month: int
    installment_months: list[int]

    def per_installment(self) -> float:
        """Amount per tax installment based on current assessment."""
        return round(self.annual_amount / len(self.installment_months), 2)


@dataclass
class TaxRateChange:
    """Anticipated change in property tax assessment.

    Properties:
        new_annual_amount: New annual tax amount
        effective_fiscal_year_start: Start date of the fiscal year when
            the new rate takes effect
    """

    new_annual_amount: float
    effective_fiscal_year_start: date


@dataclass
class InsurancePolicy:
    """Homeowner's insurance policy for escrow.

    Properties:
        annual_premium: Annual insurance premium
        renewal_month: Month when annual premium is due (1-12)
    """

    annual_premium: float
    renewal_month: int


@dataclass
class EscrowSetup:
    """Configuration for escrow analysis.

    Properties:
        current_balance: Current escrow account balance
        analysis_month: Month when annual escrow analysis is performed
        analysis_year: Year of the analysis
        tax: Property tax assessment
        insurance: Insurance policy
        cushion_months: Number of months' cushion to maintain (RESPA max: 2)
        anticipated_tax_changes: List of anticipated tax rate changes
        anticipated_insurance_premium: New insurance premium if changing
    """

    current_balance: float
    analysis_month: int
    analysis_year: int
    tax: TaxAssessment
    insurance: InsurancePolicy
    cushion_months: int = 2
    anticipated_tax_changes: list[TaxRateChange] = field(default_factory=list)
    anticipated_insurance_premium: float | None = None


@dataclass
class ProjectionMonth:
    """One month in the escrow balance projection."""

    month: int
    year: int
    deposit: float
    tax_disbursement: float
    insurance_disbursement: float
    ending_balance: float

    @property
    def total_disbursement(self) -> float:
        return self.tax_disbursement + self.insurance_disbursement


@dataclass
class AnalysisResult:
    """Result of RESPA aggregate escrow analysis."""

    required_monthly_deposit: float
    total_annual_disbursements: float
    cushion_amount: float
    shortage: float
    surplus: float
    projections: list[ProjectionMonth]
