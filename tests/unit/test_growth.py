import math

import pytest

from app.domain.formulas.growth import (
    expected_log_growth_per_trial,
    expected_terminal_bankroll,
)


def test_expected_log_growth_per_trial_is_zero_when_risk_fraction_is_zero() -> None:
    result = expected_log_growth_per_trial(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.0,
    )

    assert result == pytest.approx(0.0)


def test_expected_log_growth_per_trial_can_be_negative() -> None:
    result = expected_log_growth_per_trial(
        win_rate=0.40,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.20,
    )

    assert result < 0.0


def test_expected_terminal_bankroll_equals_initial_bankroll_when_risk_fraction_is_zero() -> None:
    result = expected_terminal_bankroll(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.0,
        trials=300,
        initial_bankroll=10_000.0,
    )

    assert result == pytest.approx(10_000.0)


def test_expected_terminal_bankroll_matches_single_trial_expectation() -> None:
    win_rate = 0.55
    reward_to_risk_ratio = 1.2
    risk_fraction = 0.02
    initial_bankroll = 10_000.0

    result = expected_terminal_bankroll(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=1,
        initial_bankroll=initial_bankroll,
    )

    expected = initial_bankroll * (
        win_rate * (1.0 + (risk_fraction * reward_to_risk_ratio))
        + (1.0 - win_rate) * (1.0 - risk_fraction)
    )

    assert result == pytest.approx(expected)
    assert math.isfinite(result)


def test_expected_log_growth_per_trial_exact_value() -> None:
    # Protects against formula regression and sign-flip mutations
    # (e.g., changing '+' to '-' in win_multiplier or log accumulation)
    result = expected_log_growth_per_trial(
        win_rate=0.5,
        reward_to_risk_ratio=2.0,
        risk_fraction=0.1,
    )

    # Expected: 0.5 * log(1.2) + 0.5 * log(0.9)
    expected = 0.5 * math.log(1.2) + 0.5 * math.log(0.9)
    assert result == pytest.approx(expected)
