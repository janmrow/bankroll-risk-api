"""
Analytical formulas for binary independent trials.
Closed-form solutions for expectancy, growth, and Kelly sizing.
"""

from app.domain.formulas.expectancy import (
    break_even_win_rate,
    edge_per_risk_unit,
    expected_return_per_trial,
)
from app.domain.formulas.growth import (
    expected_log_growth_per_trial,
    expected_terminal_bankroll,
    loss_multiplier,
    win_multiplier,
)
from app.domain.formulas.kelly import half_kelly_fraction, kelly_fraction

__all__ = [
    "break_even_win_rate",
    "edge_per_risk_unit",
    "expected_log_growth_per_trial",
    "expected_return_per_trial",
    "expected_terminal_bankroll",
    "half_kelly_fraction",
    "kelly_fraction",
    "loss_multiplier",
    "win_multiplier",
]
