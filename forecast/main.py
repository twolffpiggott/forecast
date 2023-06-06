from typing import Callable, Iterable, Union

import numpy as np

from forecast import InvestmentAssumptions, forecast_investment_values
from forecast.plot import plot_forecast, plot_multiple_forecasts
from forecast.utils import format_rand_value, format_rate, setup_logger

logger = setup_logger()


def generate_and_plot_forecasts(
    param_values: Iterable[Union[int, float]],
    param_name: str,
    label_func: Callable[[float], str],
    title: str,
    filename: str,
) -> None:
    """
    Generate forecast scenarios and plot the time series for varying parameters.

    :param param_values: Iterable of parameter values to be used in the forecasts.
    :param param_name: Name of the parameter being varied.
    :param label_func: Function to format the label for each forecast.
    :param title: Title for the plots.
    :param filename: Filename for the plots.
    """
    forecasts = []
    for value in param_values:
        forecast = forecast_investment_values(
            InvestmentAssumptions(**{**kwargs, **{param_name: value}}),
            label=label_func(value),
        )
        forecasts.append(forecast)
    plot_multiple_forecasts(forecasts, title=title, filename=filename)


if __name__ == "__main__":
    kwargs = dict(
        income_surplus=30000,
        investment_rate=0.085,
        property_valuation=3000000,
        bond_rate=0.096,
        bond_term=20,
        monthly_insurance=500,
        monthly_taxes=1500,
        monthly_levies=2000,
        transfer_duty=70000,
        lawyer_fees=70000,
        property_appreciation_rate=0.1,
        deposit=300000,
        n_years=10,
        monthly_rental_income=15000,
        property_sale_commission_rate=0.05,
        rental_escalation_rate=0.05,
        property_expenses_escalation_rate=0.05,
        inflation_rate=0.06,
        rental_management_percentage_fee=0.1,
    )
    assumptions = InvestmentAssumptions(**kwargs)
    forecast = forecast_investment_values(assumptions, label="Baseline")
    plot_forecast(forecast, assumptions, "baseline")

    # vary the deposit amount
    generate_and_plot_forecasts(
        param_values=range(0, 1000000, 250000),
        param_name="deposit",
        label_func=format_rand_value,
        title="Varying Deposit Amount",
        filename="varying_deposit",
    )

    # vary the bond rate
    # lower rate range
    generate_and_plot_forecasts(
        param_values=np.arange(0.001, 0.1, 0.025),
        param_name="bond_rate",
        label_func=format_rate,
        title="Varying Bond Rate (lower)",
        filename="varying_bond_rate_lower",
    )

    # higher rate range
    generate_and_plot_forecasts(
        param_values=np.arange(0.1, 0.2, 0.025),
        param_name="bond_rate",
        label_func=format_rate,
        title="Varying Bond Rate (higher)",
        filename="varying_bond_rate_higher",
    )

    # vary the rental income
    generate_and_plot_forecasts(
        param_values=np.arange(14000, 22000, 2000),
        param_name="monthly_rental_income",
        label_func=format_rand_value,
        title="Varying Rental Income",
        filename="varying_rental_income",
    )

    # vary the property appreciation rate
    generate_and_plot_forecasts(
        param_values=np.arange(0.04, 0.12, 0.02),
        param_name="property_appreciation_rate",
        label_func=format_rate,
        title="Varying Property Appreciation Rate",
        filename="varying_property_appreciation_rate",
    )
