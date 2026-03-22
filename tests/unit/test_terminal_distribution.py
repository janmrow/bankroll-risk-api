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


def test_binomial_log_probability_exact_value() -> None:
    # Validates raw helper logic; normalization in higher-level functions
    # can often mask underlying formula regressions.
    result = _binomial_log_probability(trials=2, wins=1, win_rate=0.5)
    assert result == pytest.approx(math.log(0.5))


def test_terminal_bankroll_quantile_max_boundary() -> None:
    # Boundary test for the 1.0 quantile to ensure index-out-of-bounds safety
    bankrolls, _ = terminal_bankroll_distribution(
        win_rate=0.5,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.1,
        trials=10,
        initial_bankroll=100.0,
    )
    result = terminal_bankroll_quantile(
        win_rate=0.5,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.1,
        trials=10,
        initial_bankroll=100.0,
        quantile=1.0,
    )
    assert result == pytest.approx(bankrolls[-1])


def test_terminal_bankroll_quantiles_exact_values() -> None:
    # Verifies exact CDF points for a known 2-trial distribution
    # to ensure calculation accuracy beyond simple sorting.
    quantiles = terminal_bankroll_quantiles(
        win_rate=0.5,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.1,
        trials=2,
        initial_bankroll=100.0,
    )
    # n=2, p=0.5: [81.0 (p=0.25), 99.0 (p=0.50), 121.0 (p=0.25)]
    assert quantiles["p05"] == pytest.approx(81.0)
    assert quantiles["p50"] == pytest.approx(99.0)
    assert quantiles["p95"] == pytest.approx(121.0)


def test_horizon_ruin_probability_exact_threshold_match() -> None:
    # Validates comparison operator boundary (<= vs <) when bankroll
    # sits exactly on the ruin threshold.
    result = horizon_ruin_probability(
        win_rate=0.5,
        reward_to_risk_ratio=1.2,
        risk_fraction=0.0,
        trials=10,
        initial_bankroll=100.0,
        ruin_threshold_fraction=1.0,  # Threshold exactly at initial bankroll
    )
    assert result == pytest.approx(1.0)


def test_p95_is_distinct_from_absolute_max_for_large_n() -> None:
    # Guards against quantile aliasing. At low n (e.g., n=2), the top bucket
    # has high probability (25%), causing p95 and max to overlap.
    # Increasing n to 20 ensures p95 hits a lower bin, validating correct index mapping.
    bankrolls, _ = terminal_bankroll_distribution(
        win_rate=0.5,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.1,
        trials=20,
        initial_bankroll=100.0,
    )
    quantiles = terminal_bankroll_quantiles(
        win_rate=0.5,
        reward_to_risk_ratio=1.0,
        risk_fraction=0.1,
        trials=20,
        initial_bankroll=100.0,
    )

    # p95 should be strictly less than the theoretical maximum at this resolution
    assert quantiles["p95"] < bankrolls[-1]
