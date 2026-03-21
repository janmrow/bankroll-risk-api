import pytest

from app.domain.formulas.kelly import half_kelly_fraction, kelly_fraction


def test_kelly_fraction_matches_closed_form() -> None:
    result = kelly_fraction(win_rate=0.55, reward_to_risk_ratio=1.2)

    expected = 0.55 - (0.45 / 1.2)
    assert result == pytest.approx(expected)


def test_kelly_fraction_is_clipped_to_zero_when_edge_is_non_positive() -> None:
    result = kelly_fraction(win_rate=0.40, reward_to_risk_ratio=1.0)

    assert result == 0.0


def test_half_kelly_fraction_is_half_of_kelly() -> None:
    full_kelly = kelly_fraction(win_rate=0.55, reward_to_risk_ratio=1.2)
    result = half_kelly_fraction(win_rate=0.55, reward_to_risk_ratio=1.2)

    assert result == pytest.approx(0.5 * full_kelly)
