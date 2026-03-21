import pytest

from app.domain.formulas.expectancy import (
    break_even_win_rate,
    edge_per_risk_unit,
    expected_return_per_trial,
)


def test_edge_per_risk_unit_matches_closed_form() -> None:
    result = edge_per_risk_unit(win_rate=0.55, reward_to_risk_ratio=1.2)

    assert result == pytest.approx((0.55 * 1.2) - 0.45)


def test_break_even_win_rate_matches_closed_form() -> None:
    result = break_even_win_rate(reward_to_risk_ratio=1.2)

    assert result == pytest.approx(1.0 / 2.2)


def test_expected_return_per_trial_equals_risk_fraction_times_edge() -> None:
    result = expected_return_per_trial(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
    )

    assert result == pytest.approx(0.02 * ((0.55 * 1.2) - 0.45))


def test_edge_per_risk_unit_can_be_negative() -> None:
    result = edge_per_risk_unit(win_rate=0.40, reward_to_risk_ratio=1.0)

    assert result < 0.0
