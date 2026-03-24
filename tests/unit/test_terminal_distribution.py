import math

import numpy as np
import pytest

from app.domain.formulas.terminal_distribution import (
    _binomial_log_probability,
    binomial_probability_mass,
    horizon_ruin_probability,
    ruin_threshold_bankroll,
    terminal_bankroll_distribution,
    terminal_bankroll_quantile,
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
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
        trials=300,
        initial_bankroll=10_000.0,
    )
    quantiles = terminal_bankroll_quantiles(bankrolls, probabilities)
    assert quantiles["p05"] <= quantiles["p50"] <= quantiles["p95"]


def test_ruin_threshold_bankroll_scales_from_initial_bankroll() -> None:
    result = ruin_threshold_bankroll(initial_bankroll=10_000.0, ruin_threshold_fraction=0.25)
    assert result == pytest.approx(2_500.0)


def test_horizon_ruin_probability_is_zero_for_zero_threshold_fraction() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.55,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.02,
        trials=300,
        initial_bankroll=10_000.0,
    )
    result = horizon_ruin_probability(
        bankrolls=bankrolls,
        probabilities=probabilities,
        initial_bankroll=10_000.0,
        ruin_threshold_fraction=0.0,
    )
    assert result == pytest.approx(0.0)


def test_binomial_log_probability_exact_value() -> None:
    result = _binomial_log_probability(trials=2, wins=1, win_rate=0.5)
    assert result == pytest.approx(math.log(0.5))


def test_terminal_bankroll_quantile_max_boundary() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.5, reward_to_risk_ratio=1.0, risk_fraction=0.1, trials=10, initial_bankroll=100.0
    )
    result = terminal_bankroll_quantile(bankrolls, probabilities, quantile=1.0)
    assert result == pytest.approx(bankrolls[-1])


def test_terminal_bankroll_quantiles_exact_values() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.5, reward_to_risk_ratio=1.0, risk_fraction=0.1, trials=2, initial_bankroll=100.0
    )
    quantiles = terminal_bankroll_quantiles(bankrolls, probabilities)
    assert quantiles["p05"] == pytest.approx(81.0)
    assert quantiles["p50"] == pytest.approx(99.0)
    assert quantiles["p95"] == pytest.approx(121.0)


def test_horizon_ruin_probability_exact_threshold_match() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.5, reward_to_risk_ratio=1.2, risk_fraction=0.0, trials=10, initial_bankroll=100.0
    )
    result = horizon_ruin_probability(
        bankrolls=bankrolls,
        probabilities=probabilities,
        initial_bankroll=100.0,
        ruin_threshold_fraction=1.0,
    )
    assert result == pytest.approx(1.0)


def test_p95_is_distinct_from_absolute_max_for_large_n() -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=0.5, reward_to_risk_ratio=1.0, risk_fraction=0.1, trials=20, initial_bankroll=100.0
    )
    quantiles = terminal_bankroll_quantiles(bankrolls, probabilities)
    assert quantiles["p95"] < bankrolls[-1]
