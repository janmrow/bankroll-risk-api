from math import exp, lgamma, log

import numpy as np
from numpy.typing import NDArray

from app.domain.formulas.growth import loss_multiplier, win_multiplier

FloatArray = NDArray[np.float64]  # pragma: no mutate


def _binomial_log_probability(trials: int, wins: int, win_rate: float) -> float:
    loss_rate = 1.0 - win_rate
    return (
        lgamma(trials + 1)
        - lgamma(wins + 1)
        - lgamma(trials - wins + 1)
        + (wins * log(win_rate))
        + ((trials - wins) * log(loss_rate))
    )


def binomial_probability_mass(trials: int, win_rate: float) -> FloatArray:
    probabilities = np.zeros(trials + 1, dtype=np.float64)
    if win_rate == 0.0:
        probabilities[0] = 1.0
        return probabilities
    if win_rate == 1.0:
        probabilities[-1] = 1.0
        return probabilities

    probabilities = np.array(
        [
            exp(_binomial_log_probability(trials=trials, wins=wins, win_rate=win_rate))
            for wins in range(trials + 1)
        ],
        dtype=np.float64,
    )
    probabilities /= probabilities.sum()  # pragma: no mutate
    return probabilities


def terminal_bankroll_for_wins(
    initial_bankroll: float,
    risk_fraction: float,
    reward_to_risk_ratio: float,
    trials: int,
    wins: int,
) -> float:
    return (
        initial_bankroll
        * (win_multiplier(risk_fraction, reward_to_risk_ratio) ** wins)
        * (loss_multiplier(risk_fraction) ** (trials - wins))
    )


def terminal_bankroll_distribution(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
) -> tuple[FloatArray, FloatArray]:
    bankrolls = np.array(
        [
            terminal_bankroll_for_wins(
                initial_bankroll=initial_bankroll,
                risk_fraction=risk_fraction,
                reward_to_risk_ratio=reward_to_risk_ratio,
                trials=trials,
                wins=wins,
            )
            for wins in range(trials + 1)
        ],
        dtype=np.float64,
    )
    probabilities = binomial_probability_mass(trials=trials, win_rate=win_rate)
    return bankrolls, probabilities


def terminal_bankroll_quantile(
    bankrolls: FloatArray,
    probabilities: FloatArray,
    quantile: float,
) -> float:
    cumulative = np.cumsum(probabilities)
    index = int(np.searchsorted(cumulative, quantile, side="left"))
    index = min(index, len(bankrolls) - 1)
    return float(bankrolls[index])


def terminal_bankroll_quantiles(
    bankrolls: FloatArray,
    probabilities: FloatArray,
) -> dict[str, float]:
    return {
        "p05": terminal_bankroll_quantile(bankrolls, probabilities, 0.05),
        "p50": terminal_bankroll_quantile(bankrolls, probabilities, 0.50),
        "p95": terminal_bankroll_quantile(bankrolls, probabilities, 0.95),
    }


def ruin_threshold_bankroll(
    initial_bankroll: float,
    ruin_threshold_fraction: float,
) -> float:
    return initial_bankroll * ruin_threshold_fraction


def horizon_ruin_probability(
    bankrolls: FloatArray,
    probabilities: FloatArray,
    initial_bankroll: float,
    ruin_threshold_fraction: float,
) -> float:
    threshold = ruin_threshold_bankroll(
        initial_bankroll=initial_bankroll,
        ruin_threshold_fraction=ruin_threshold_fraction,
    )
    raw_probability = probabilities[bankrolls <= threshold].sum()
    return float(np.clip(raw_probability, 0.0, 1.0))  # pragma: no mutate
