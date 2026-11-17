"""Deterministic financial education tools."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, getcontext
from typing import Any


getcontext().prec = 28
MAX_MONTHS = 1200
SEBI_RUPEE_COST_AVERAGING_SOURCE = (
    "https://investor.sebi.gov.in/ssis/investing-through-mutual-funds-03.html"
)


def _decimal(value: Any, name: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError(f"{name} must be a finite number.") from error
    if not number.is_finite():
        raise ValueError(f"{name} must be a finite number.")
    return number


def _positive(value: Any, name: str) -> Decimal:
    number = _decimal(value, name)
    if number <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return number


def _number(value: Decimal) -> int | float:
    result = float(value)
    return int(result) if result.is_integer() else result


def _validate_months(years: Any) -> int:
    duration = _positive(years, "years")
    if duration != duration.to_integral_value():
        raise ValueError("years must be a whole number of years.")
    months = int(duration * 12)
    if months > MAX_MONTHS:
        raise ValueError(f"years must not exceed {MAX_MONTHS // 12}.")
    return months


def sip_rupee_cost_averaging(
    monthly_sip: Any,
    navs: list[Any] | None = None,
    *,
    annual_return_percent: Any | None = None,
    years: Any | None = None,
    yearly_step_up_percent: Any = 0,
) -> dict[str, Any]:
    """Calculate NAV-based SIP results or an assumed-return projection.

    With ``navs``, each contribution is made at the supplied monthly NAV.
    With ``annual_return_percent`` and ``years``, contributions are made at
    the end of each month and the annual return is converted to an effective
    monthly rate. The projection does not represent historical NAVs or units.
    """
    investment = _positive(monthly_sip, "monthly_sip")
    step_up = _decimal(yearly_step_up_percent, "yearly_step_up_percent")
    if step_up < 0 or step_up > 1000:
        raise ValueError("yearly_step_up_percent must be between 0 and 1000.")

    if navs is not None:
        if annual_return_percent is not None or years is not None:
            raise ValueError("Provide either navs or annual return assumptions, not both.")
        if not navs:
            raise ValueError("navs must contain at least one positive NAV.")
        nav_values = [_positive(nav, "NAV") for nav in navs]
        total_invested = Decimal("0")
        total_units = Decimal("0")
        monthly_breakdown = []
        for month, nav in enumerate(nav_values, start=1):
            units = investment / nav
            total_invested += investment
            total_units += units
            monthly_breakdown.append(
                {
                    "month": month,
                    "investment": _number(investment),
                    "nav": _number(nav),
                    "units_bought": _number(units),
                }
            )
        final_value = total_units * nav_values[-1]
        return {
            "mode": "nav_based",
            "monthly_breakdown": monthly_breakdown,
            "total_invested": _number(total_invested),
            "total_units": _number(total_units),
            "average_cost_per_unit": _number(total_invested / total_units),
            "final_nav": _number(nav_values[-1]),
            "final_value": _number(final_value),
            "gain_or_loss": _number(final_value - total_invested),
            "illustrative": False,
        }

    if annual_return_percent is None or years is None:
        raise ValueError("Provide navs, or both annual_return_percent and years.")
    annual_return = _decimal(annual_return_percent, "annual_return_percent")
    if annual_return <= -100 or annual_return > 1000:
        raise ValueError("annual_return_percent must be greater than -100 and at most 1000.")
    months = _validate_months(years)
    monthly_rate = (Decimal("1") + annual_return / Decimal("100")) ** (
        Decimal("1") / Decimal("12")
    ) - Decimal("1")
    balance = Decimal("0")
    total_invested = Decimal("0")
    monthly_breakdown = []
    for month in range(1, months + 1):
        contribution = investment * (
            (Decimal("1") + step_up / Decimal("100"))
            ** Decimal((month - 1) // 12)
        )
        balance = (balance + contribution) * (Decimal("1") + monthly_rate)
        total_invested += contribution
        monthly_breakdown.append(
            {
                "month": month,
                "investment": _number(contribution),
                "estimated_value": _number(balance),
            }
        )
    return {
        "mode": "assumed_return_projection",
        "monthly_breakdown": monthly_breakdown,
        "total_invested": _number(total_invested),
        "estimated_final_value": _number(balance),
        "estimated_gain_or_loss": _number(balance - total_invested),
        "annual_return_percent": _number(annual_return),
        "years": int(years),
        "yearly_step_up_percent": _number(step_up),
        "contribution_timing": "end of each month",
        "illustrative": True,
        "units_note": "No actual units or NAV-based average cost are calculated.",
    }
