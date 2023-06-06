import logging
from dataclasses import dataclass
from typing import List, Union

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ForecastScenario:
    """
    A dataclass representing a forecasted financial scenario.

    :param label: The label for the scenario.
    :param property_values: The forecasted monthly total values of the property investment over a given period.
    :param investment_values: The forecasted monthly total values of the stock market investment over a given period.
    """

    label: str
    property_values: List[float]
    investment_values: List[float]


@dataclass(frozen=True)
class InvestmentAssumptions:
    """
    This dataclass represents the assumptions for an investment scenario comparison.

    It includes parameters for property investment and stock market investment.

    TODO escalation for income surplus?

    :param income_surplus: Monthly income surplus available for investment.
    :param investment_rate: Expected annual return rate in the stock market.
    :param property_valuation: Initial value of the property.
    :param bond_rate: Annual interest rate of the bond.
    :param bond_term: Term of the bond in years.
    :param monthly_insurance: Monthly cost for home owner's insurance.
    :param monthly_taxes: Monthly cost for property taxes.
    :param monthly_levies: Monthly cost for levies.
    :param transfer_duty: One-time cost for transfer duty.
    :param lawyer_fees: One-time cost for lawyer's fees.
    :param property_appreciation_rate: Expected annual property appreciation rate.
    :param deposit: Initial deposit for the property.
    :param n_years: Number of years for the investment scenario.
    :param monthly_rental_income: Monthly rental income from property
    :param property_sale_commission_rate: Commission percent for property sale
    :param rental_escalation_rate: Annual escalation rate for rental.
    :param property_expenses_escalation_rate: Annual escalation rate for property expenses.
    :param inflation_rate: The annual inflation rate used to calculate real values.
    :param rental_management_percentage_fee: The (optional) percentage of the coming year's
        total rental income charged by the agent for procurement and management
    """

    income_surplus: float
    investment_rate: float
    property_valuation: float
    bond_rate: float
    bond_term: int
    monthly_insurance: float
    monthly_taxes: float
    monthly_levies: float
    transfer_duty: float
    lawyer_fees: float
    property_appreciation_rate: float
    deposit: float
    n_years: int
    monthly_rental_income: float
    property_sale_commission_rate: float
    rental_escalation_rate: float
    property_expenses_escalation_rate: float
    inflation_rate: float
    rental_management_percentage_fee: Union[float, None] = None


def calculate_bond_repayment(principal: float, r: float, n: int) -> float:
    """
    Calculate the monthly repayment for a bond.

    :param principal: The principal amount of the bond.
    :param r: The annual interest rate of the bond (as a decimal, e.g., 5% is 0.05).
    :param n: The term of the bond in months.
    :return: The monthly repayment amount.
    """
    r_monthly = r / 12
    monthly_repayment = (
        principal * r_monthly * (1 + r_monthly) ** n / ((1 + r_monthly) ** n - 1)
    )
    return monthly_repayment


def calculate_remaining_bond_balance(
    principal: float, rate: float, n_payments: int, monthly_payment_amount: float
) -> float:
    """
    Calculate the remaining balance of a bond after a certain number of payments.

    :param principal: The original amount of the bond.
    :param rate: The annual interest rate of the bond.
    :param n_payments: The number of payments that have been made.
    :param monthly_payment_amount: The amount of the monthly payments.
    :return: The remaining balance of the bond.
    """
    monthly_rate = rate / 12
    remaining_balance = (
        principal * (1 + monthly_rate) ** n_payments
        - monthly_payment_amount * ((1 + monthly_rate) ** n_payments - 1) / monthly_rate
    )
    return remaining_balance


def forecast_investment_values(
    assumptions: InvestmentAssumptions,
    label: str,
) -> ForecastScenario:
    """
    Forecasts the total value of investment in property and a low-cost index fund over time.

    The function takes an InvestmentAssumptions object, simulates the investment scenarios
    for property and stocks over a given number of years, and returns the monthly total
    value of each investment over the given period.

    :param assumptions: An InvestmentAssumptions object containing the assumptions for the investment scenarios.
    :param label: A label for the forecast scenario (e.g. "R300 000 deposit")
    :return: A ForecastScenario object representing the monthly total values of the property and stock investments.
    """
    logger.info("Forecasting values for '%s' scenario", label)
    n_months = assumptions.n_years * 12
    bond_repayment = calculate_bond_repayment(
        assumptions.property_valuation - assumptions.deposit,
        assumptions.bond_rate,
        assumptions.bond_term * 12,
    )
    monthly_property_expenses = (
        assumptions.monthly_insurance
        + assumptions.monthly_taxes
        + assumptions.monthly_levies
    )
    property_costs = assumptions.transfer_duty + assumptions.lawyer_fees
    monthly_rental_income = assumptions.monthly_rental_income
    net_monthly_rental_income = _calculate_net_monthly_rental_income(
        monthly_rental_income, assumptions.rental_management_percentage_fee
    )
    monthly_investment_after_expenses = (
        assumptions.income_surplus
        + net_monthly_rental_income
        - bond_repayment
        - monthly_property_expenses
    )
    monthly_investment_in_stocks = assumptions.income_surplus

    property_valuations = [assumptions.property_valuation]
    investment_after_expenses_total_value = [monthly_investment_after_expenses]

    outstanding_bond_balance = calculate_remaining_bond_balance(
        principal=assumptions.property_valuation - assumptions.deposit,
        rate=assumptions.bond_rate,
        n_payments=0,
        monthly_payment_amount=bond_repayment,
    )
    property_total_value = [
        (1 - assumptions.property_sale_commission_rate)
        * (
            assumptions.property_valuation
            + monthly_investment_after_expenses
            - outstanding_bond_balance
        )
    ]
    investment_total_value = [
        monthly_investment_in_stocks + property_costs + assumptions.deposit
    ]
    property_total_value_real = [property_total_value[0]]
    investment_total_value_real = [investment_total_value[0]]

    # Convert annual inflation rate to monthly
    monthly_inflation_rate = (1 + assumptions.inflation_rate) ** (1 / 12) - 1

    # Simulating property value and investment in stocks over time
    for i in range(1, n_months):
        # Property scenario
        property_valuation = property_valuations[-1] * (
            1 + assumptions.property_appreciation_rate / 12
        )
        investment_after_expenses_value = (
            investment_after_expenses_total_value[-1]
            * (1 + assumptions.investment_rate / 12)
            + monthly_investment_after_expenses
        )
        property_valuations.append(property_valuation)
        investment_after_expenses_total_value.append(investment_after_expenses_value)

        # Calculate outstanding bond balance
        outstanding_bond_balance = calculate_remaining_bond_balance(
            principal=assumptions.property_valuation - assumptions.deposit,
            rate=assumptions.bond_rate,
            n_payments=i,
            monthly_payment_amount=bond_repayment,
        )

        # Property total value reduced by outstanding bond balance
        property_total_value.append(
            (1 - assumptions.property_sale_commission_rate)
            * (
                property_valuation
                + investment_after_expenses_value
                - outstanding_bond_balance
            )
        )

        # Escalate property expenses and rental income annually
        if i % 12 == 0:
            monthly_property_expenses *= (
                1 + assumptions.property_expenses_escalation_rate
            )
            monthly_rental_income *= 1 + assumptions.rental_escalation_rate
            net_monthly_rental_income = _calculate_net_monthly_rental_income(
                monthly_rental_income, assumptions.rental_management_percentage_fee
            )

            # Recalculate monthly investment after expenses with updated property expenses and rental income
            monthly_investment_after_expenses = (
                assumptions.income_surplus
                + net_monthly_rental_income
                - bond_repayment
                - monthly_property_expenses
            )
            if monthly_investment_after_expenses <= 0:
                logger.warning(
                    "Monthly investment after expenses is %f",
                    monthly_investment_after_expenses,
                )

        # Investment scenario
        investment_in_stocks = (
            investment_total_value[-1] * (1 + assumptions.investment_rate / 12)
            + assumptions.income_surplus
        )
        investment_total_value.append(investment_in_stocks)

        # Adjust for inflation at the end of each month
        inflation_adjustment = (1 + monthly_inflation_rate) ** i
        property_total_value_real.append(property_total_value[i] / inflation_adjustment)
        investment_total_value_real.append(
            investment_total_value[i] / inflation_adjustment
        )

    return ForecastScenario(
        label=label,
        property_values=property_total_value_real,
        investment_values=investment_total_value_real,
    )


def _calculate_net_monthly_rental_income(
    monthly_rental_income: float, rental_management_percentage_fee: Union[float, None]
) -> float:
    if rental_management_percentage_fee is not None:
        monthly_management_fee = (
            rental_management_percentage_fee * monthly_rental_income
        )
        monthly_rental_income -= monthly_management_fee
    return monthly_rental_income
