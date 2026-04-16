"""Insurance disbursement calculations."""

from .models import InsurancePolicy


def compute_monthly_insurance_disbursements(
    policy: InsurancePolicy,
    start_month: int,
    start_year: int,
    anticipated_premium: float | None = None,
) -> list[tuple[int, int, float]]:
    """Compute insurance disbursement for each month in a 12-month projection.

    Insurance premium is paid annually in the renewal month.
    If anticipated_premium is provided, it's used for the renewal that
    falls within the projection period.

    Returns:
        List of (month, year, disbursement_amount) tuples for 12 months.
    """
    premium = (
        anticipated_premium if anticipated_premium is not None else policy.annual_premium
    )

    result = []
    for i in range(12):
        month = (start_month - 1 + i) % 12 + 1
        year = start_year + (start_month - 1 + i) // 12

        if month == policy.renewal_month:
            result.append((month, year, premium))
        else:
            result.append((month, year, 0.0))

    return result
