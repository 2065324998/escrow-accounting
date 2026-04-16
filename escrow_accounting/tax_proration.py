"""Property tax proration across fiscal year boundaries."""

from datetime import date

from .models import TaxAssessment, TaxRateChange


def compute_monthly_tax_disbursements(
    tax: TaxAssessment,
    start_month: int,
    start_year: int,
    anticipated_changes: list[TaxRateChange],
) -> list[tuple[int, int, float]]:
    """Compute tax disbursement for each month in a 12-month projection period.

    Property taxes are assessed per fiscal year, so the tax amount for each
    month depends on which fiscal year that month falls in. When the projection
    period spans a fiscal year boundary with a rate change, each installment
    payment should reflect the rate for its respective fiscal year.

    Args:
        tax: Current tax assessment
        start_month: First month of the 12-month projection
        start_year: Year of the first month
        anticipated_changes: Expected future tax rate changes

    Returns:
        List of (month, year, disbursement_amount) tuples for 12 months.
        Disbursement is non-zero only in installment months.
    """
    result = []

    for i in range(12):
        month = (start_month - 1 + i) % 12 + 1
        year = start_year + (start_month - 1 + i) // 12

        # Determine which fiscal year this month belongs to
        fy_start = _fiscal_year_for_month(month, year, tax.fiscal_year_start_month)

        # Get applicable annual tax amount for this fiscal year
        annual = _applicable_tax_amount(
            tax.annual_amount, fy_start, anticipated_changes
        )

        # Disburse in installment months only
        if month in tax.installment_months:
            amount = round(annual / len(tax.installment_months), 2)
        else:
            amount = 0.0

        result.append((month, year, amount))

    return result


def _fiscal_year_for_month(month: int, year: int, fy_start_month: int) -> date:
    """Determine the start of the fiscal year containing the given month.

    Example: if fiscal year starts in July (month 7), then:
        - October 2025 -> FY starting July 2025
        - March 2025   -> FY starting July 2024
    """
    return date(year, fy_start_month, 1)


def _applicable_tax_amount(
    base_amount: float,
    fiscal_year_start: date,
    changes: list[TaxRateChange],
) -> float:
    """Get the tax amount for a given fiscal year.

    Checks anticipated rate changes and returns the most recent
    applicable amount for the fiscal year.
    """
    amount = base_amount
    for change in sorted(changes, key=lambda c: c.effective_fiscal_year_start):
        if change.effective_fiscal_year_start < fiscal_year_start:
            amount = change.new_annual_amount
    return amount
