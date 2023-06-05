import logging
import sys
from typing import Union


def setup_logger(logger_name: Union[str, None], level: Union[str, int] = logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def format_rand_value(amount: float) -> str:
    """
    >>> format_rand_value(3100000.28)
    'R3,100,000'
    """
    return f"R{format(int(amount), ',')}"


def format_rate(rate: float) -> str:
    """
    >>> format_rate(0.12345)
    '12.35%'
    """
    return f"{100*rate:.2f}%"
