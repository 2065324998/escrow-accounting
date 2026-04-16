"""RESPA aggregate escrow analysis.

Implements the aggregate accounting method required by the Real Estate
Settlement Procedures Act (RESPA) for annual escrow account analysis.
The analysis projects the account balance month-by-month to determine
the required monthly deposit and identify any shortage or surplus.
"""

from .models import EscrowSetup, AnalysisResult, ProjectionMonth
from .tax_proration import compute_monthly_tax_disbursements
from .insurance import compute_monthly_insurance_disbursements

# Cap the required starting balance at this multiple of the cushion
# to prevent over-collection per the servicer's escrow policy
STARTING_BALANCE_CUSHION_LIMIT = 1.5


def perform_analysis(setup: EscrowSetup) -> AnalysisResult:
    """Perform annual escrow analysis.

    Analyzes the escrow account to determine the required monthly
    deposit for the upcoming year based on anticipated disbursements,
    current balance, and cushion requirements.
    """
    # Step 1: Project disbursements
    tax_disb = compute_monthly_tax_disbursements(
        setup.tax,
        setup.analysis_month,
        setup.analysis_year,
        setup.anticipated_tax_changes,
    )

    insurance_disb = compute_monthly_insurance_disbursements(
        setup.insurance,
        setup.analysis_month,
        setup.analysis_year,
        setup.anticipated_insurance_premium,
    )

    # Combine monthly disbursements
    monthly_total_disb = []
    for i in range(12):
        monthly_total_disb.append(tax_disb[i][2] + insurance_disb[i][2])

    total_annual_disb = round(sum(monthly_total_disb), 2)

    # Compute base monthly deposit and cushion
    base_deposit = round(total_annual_disb / 12, 2)

    cushion = round(base_deposit * setup.cushion_months, 2)

    # Required monthly deposit: base plus cushion spread over 12 months
    required_deposit = round(base_deposit + cushion / 12, 2)

    # Shortage/surplus: compare cushion to current balance
    shortage = round(max(0, cushion - setup.current_balance), 2)
    surplus = round(max(0, setup.current_balance - cushion), 2)

    if shortage > 0:
        final_deposit = round(required_deposit + shortage / 12, 2)
    elif surplus > 50:
        final_deposit = round(required_deposit - surplus / 12, 2)
    else:
        final_deposit = required_deposit

    # Build month-by-month projection with final deposit
    projections = _build_projections(
        setup, tax_disb, insurance_disb, final_deposit
    )

    return AnalysisResult(
        required_monthly_deposit=final_deposit,
        total_annual_disbursements=total_annual_disb,
        cushion_amount=cushion,
        shortage=shortage,
        surplus=surplus,
        projections=projections,
    )


def _build_projections(
    setup: EscrowSetup,
    tax_disb: list[tuple[int, int, float]],
    insurance_disb: list[tuple[int, int, float]],
    monthly_deposit: float,
) -> list[ProjectionMonth]:
    """Build month-by-month projection of escrow balance."""
    projections = []
    balance = setup.current_balance

    for i in range(12):
        month = tax_disb[i][0]
        year = tax_disb[i][1]
        tax_amount = tax_disb[i][2]
        ins_amount = insurance_disb[i][2]

        balance = round(balance + monthly_deposit - tax_amount - ins_amount, 2)

        projections.append(
            ProjectionMonth(
                month=month,
                year=year,
                deposit=monthly_deposit,
                tax_disbursement=tax_amount,
                insurance_disbursement=ins_amount,
                ending_balance=balance,
            )
        )

    return projections
