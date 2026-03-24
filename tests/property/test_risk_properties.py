import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.domain.formulas import (
    edge_per_risk_unit,
    expected_terminal_bankroll,
    horizon_ruin_probability,
    kelly_fraction,
    terminal_bankroll_distribution,
    terminal_bankroll_quantiles,
)

PROBABILITY = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
REWARD_TO_RISK = st.floats(min_value=0.1, max_value=3.0, allow_nan=False, allow_infinity=False)
RISK_FRACTION = st.floats(min_value=0.0, max_value=0.25, allow_nan=False, allow_infinity=False)
TRIALS = st.integers(min_value=1, max_value=60)
INITIAL_BANKROLL = st.floats(
    min_value=1.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False
)
RUIN_THRESHOLD = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
    ruin_threshold_fraction=RUIN_THRESHOLD,
)
def test_horizon_ruin_probability_is_bounded(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
    ruin_threshold_fraction: float,
) -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )
    result = horizon_ruin_probability(
        bankrolls=bankrolls,
        probabilities=probabilities,
        initial_bankroll=initial_bankroll,
        ruin_threshold_fraction=ruin_threshold_fraction,
    )
    assert 0.0 <= result <= 1.0
    assert not np.isnan(result)


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
)
def test_terminal_bankroll_quantiles_are_ordered(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
) -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )
    quantiles = terminal_bankroll_quantiles(bankrolls, probabilities)
    assert quantiles["p05"] <= quantiles["p50"] <= quantiles["p95"]


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
)
def test_expected_terminal_bankroll_is_positive(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
) -> None:
    result = expected_terminal_bankroll(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )
    assert result > 0.0


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
    threshold_a=RUIN_THRESHOLD,
    threshold_b=RUIN_THRESHOLD,
)
def test_higher_ruin_threshold_does_not_reduce_ruin_probability(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
    threshold_a: float,
    threshold_b: float,
) -> None:
    threshold_low, threshold_high = sorted((threshold_a, threshold_b))
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )
    ruin_low = horizon_ruin_probability(bankrolls, probabilities, initial_bankroll, threshold_low)
    ruin_high = horizon_ruin_probability(bankrolls, probabilities, initial_bankroll, threshold_high)
    assert ruin_high >= ruin_low - 1e-12


@settings(max_examples=100, deadline=None)
@given(
    probability_a=PROBABILITY,
    probability_b=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
    ruin_threshold_fraction=RUIN_THRESHOLD,
)
def test_higher_win_rate_does_not_increase_ruin_probability(
    probability_a: float,
    probability_b: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
    ruin_threshold_fraction: float,
) -> None:
    low_win_rate, high_win_rate = sorted((probability_a, probability_b))

    bankrolls_low, prob_low = terminal_bankroll_distribution(
        low_win_rate, reward_to_risk_ratio, risk_fraction, trials, initial_bankroll
    )
    ruin_low = horizon_ruin_probability(
        bankrolls_low, prob_low, initial_bankroll, ruin_threshold_fraction
    )

    bankrolls_high, prob_high = terminal_bankroll_distribution(
        high_win_rate, reward_to_risk_ratio, risk_fraction, trials, initial_bankroll
    )
    ruin_high = horizon_ruin_probability(
        bankrolls_high, prob_high, initial_bankroll, ruin_threshold_fraction
    )

    assert ruin_high <= ruin_low + 1e-12


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
)
def test_kelly_is_clipped_to_zero_when_edge_is_non_positive(
    win_rate: float,
    reward_to_risk_ratio: float,
) -> None:
    edge = edge_per_risk_unit(win_rate=win_rate, reward_to_risk_ratio=reward_to_risk_ratio)
    kelly = kelly_fraction(win_rate=win_rate, reward_to_risk_ratio=reward_to_risk_ratio)
    if edge <= 0.0:
        assert kelly == 0.0
    else:
        assert kelly >= 0.0


@settings(max_examples=100, deadline=None)
@given(
    win_rate=PROBABILITY,
    reward_to_risk_ratio=REWARD_TO_RISK,
    risk_fraction=RISK_FRACTION,
    trials=TRIALS,
    initial_bankroll=INITIAL_BANKROLL,
)
def test_distribution_aggregation_matches_expected_terminal_bankroll(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
) -> None:
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )
    expected_from_distribution = float(np.dot(bankrolls, probabilities))
    expected_from_formula = expected_terminal_bankroll(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
        trials=trials,
        initial_bankroll=initial_bankroll,
    )

    assert float(np.sum(probabilities)) == pytest.approx(1.0)
    assert expected_from_distribution == pytest.approx(expected_from_formula, rel=1e-10, abs=1e-8)
