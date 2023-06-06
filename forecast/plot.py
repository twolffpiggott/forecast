import math
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from forecast import ForecastScenario, InvestmentAssumptions
from forecast.utils import format_rand_value, format_rate


def annotate_end_of_line(
    ax: Axes,
    line: Line2D,
    values: List[float],
    other_final_value: Optional[float] = None,
) -> None:
    """
    Annotate the end of a line plot.

    :param ax: The Axes object to annotate.
    :param line: The Line2D object representing the line plot.
    :param values: The y-values of the line plot.
    :param other_final_value: The final y-value of the other line plot.
    """
    final_value = values[-1]
    annotation_text = format_rand_value(final_value)

    if other_final_value is not None and final_value > other_final_value:
        percentage_difference = (
            (final_value - other_final_value) / other_final_value
        ) * 100
        annotation_text += f" (+{percentage_difference:.2f}%)"

    ax.annotate(
        annotation_text,
        xy=(len(values), final_value),
        xytext=(10, 10),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->"),
        color=line.get_color(),
    )


def plot_forecast(
    forecast: ForecastScenario,
    assumptions: InvestmentAssumptions,
    filename: str,
    output_dir: str = "plots",
    dpi: int = 300,
):
    """
    Plot a given forecast scenario.

    :param forecast: The ForecastScenario to plot.
    :param assumptions: The InvestmentAssumptions used to create the forecast.
    :param filename: The filename of the PNG file to save.
    :param output_dir: The directory in which to save plots.
    :param dpi: DPI for saved plots.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # First subplot for the forecasts
    ax1.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, p: format_rand_value(x))
    )
    ax1.set_xlabel("Months")
    ax1.set_ylabel("Value")

    (property_line,) = ax1.plot(forecast.property_values, label="Property Scenario")
    (investment_line,) = ax1.plot(
        forecast.investment_values, label="Investment Scenario"
    )

    ax1.legend(loc="upper left")
    for label in ax1.get_yticklabels():
        label.set_rotation(45)

    annotate_end_of_line(
        ax1,
        property_line,
        forecast.property_values,
        other_final_value=forecast.investment_values[-1],
    )
    annotate_end_of_line(
        ax1,
        investment_line,
        forecast.investment_values,
        other_final_value=forecast.property_values[-1],
    )

    # Second subplot for the assumptions
    ax2.axis("off")  # Hide all axes for the assumptions plot

    # Create a string containing all the assumptions
    assumptions_text = "\n".join(
        [
            f"{key}: {format_rate(value)}"
            if "rate" in key or "percentage" in key
            else f"{key}: {format_rand_value(value)}"
            if "term" not in key and "years" not in key
            else f"{key}: {value} years"
            for key, value in assumptions.__dict__.items()
        ]
    )

    # Show the assumptions in the second subplot
    ax2.text(0, 1, assumptions_text, fontsize=10, va="top")

    # Show the heading above the assumptions text
    ax2.text(0, 1, "Investment Assumptions:", fontsize=12, va="bottom")

    # Set the title for the whole figure
    plt.suptitle(forecast.label)

    plt.tight_layout()
    _savefig(output_dir, filename, dpi)


def plot_multiple_forecasts(
    forecasts: List[ForecastScenario],
    title: str,
    filename: str,
    output_dir: str = "plots",
    dpi: int = 300,
):
    """
    Plot multiple forecast scenarios.

    :param forecasts: List of ForecastScenario objects to plot.
    :param title: The title of the plot
    :param filename: The filename of the PNG file to save.
    :param output_dir: The directory in which to save plots.
    :param dpi: DPI for saved plots.
    """
    n = len(forecasts)
    n_cols = math.ceil(math.sqrt(n))
    n_rows = math.ceil(n / n_cols)
    fig, axs = plt.subplots(
        n_rows, n_cols, figsize=(10 * n_cols, 5 * n_rows), sharex=True, sharey=True
    )

    axs = axs.flatten()

    for i, scenario in enumerate(forecasts):
        axs[i].yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, p: format_rand_value(x))
        )
        axs[i].set_xlabel("Months")
        axs[i].set_ylabel("Value")

        (property_line,) = axs[i].plot(
            scenario.property_values, label="Property Scenario"
        )
        (investment_line,) = axs[i].plot(
            scenario.investment_values, label="Investment Scenario"
        )

        axs[i].set_title(scenario.label)
        axs[i].legend(loc="upper left")

        for label in axs[i].get_yticklabels():
            label.set_rotation(45)

        annotate_end_of_line(
            axs[i],
            property_line,
            scenario.property_values,
            other_final_value=scenario.investment_values[-1],
        )
        annotate_end_of_line(
            axs[i],
            investment_line,
            scenario.investment_values,
            other_final_value=scenario.property_values[-1],
        )

    # Remove unused subplots
    for j in range(i + 1, n_rows * n_cols):
        fig.delaxes(axs[j])

    plt.suptitle(title)
    plt.tight_layout()
    _savefig(output_dir, filename, dpi)


def _savefig(output_dir: Path, filename: str, dpi: int):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_path / f"{filename}.png", dpi=dpi)
