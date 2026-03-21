import numpy as np
import pytest

from app.domain.formulas.terminal_distribution import (
    binomial_probability_mass,
    horizon_ruin_probability,
    ruin_threshold_bankroll,
    terminal_bankroll_distribution,
    terminal_bankroll_quantiles,
)


def test_binomial_probability_mass_sums_to_one() -> None:
    probabilities = binomial_probability_mass(trials=50, win_rate=0.55)

    assert float(np.sum(probabilities)) == pytest.approx(1.0)


def test_binomial_probability_mass_handles_boundary_win_rates() -> None:
    probabilities_zero = binomial_probability_mass(trials=10, win_rate=0.0)
    probabilities_one = binomial_probability_mass(trials=10, win_rate=1.0)

    assert probabilities_zero[0] == pytest.approx(1.0)
    assert probabilities_zero[1:].sum() == pytest.approx(0.0)

    assert probabilities_one[-1] == pytest.approx(1.0)
    assert probabilities_one[:-1].sum() == pytest.approx(0.0)


def test_terminal_bankroll_distribution_has_trials_plus_one_outcomes() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
        trials=25,
        initial_bankroll=10_000.0,
    )

    assert len(bankrolls) == 26
    assert len(probabilities) == 26


def test_terminal_bankroll_quantiles_are_ordered() -> None:
    quantiles = terminal_bankroll_quantiles(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
        trials=300,
        initial_bankroll=10_000.0,
    )

    assert quantiles["p05"] <= quantiles["p50"] <= quantiles["p95"]


def test_ruin_threshold_bankroll_scales_from_initial_bankroll() -> None:
    result = ruin_threshold_bankroll(
        initial_bankroll=10_000.0,
        ruin_threshold_fraction=0.25,
    )

    assert result == pytest.approx(2_500.0)


def test_horizon_ruin_probability_is_zero_for_zero_threshold_fraction() -> None:
    result = horizon_ruin_probability(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
        trials=300,
        initial_bankroll=10_000.0,
        ruin_threshold_fraction=0.0,
    )

    assert result == pytest.approx(0.0)
