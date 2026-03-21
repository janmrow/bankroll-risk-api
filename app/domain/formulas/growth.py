import math

from app.domain.formulas.expectancy import expected_return_per_trial


def win_multiplier(risk_fraction: float, reward_to_risk_ratio: float) -> float:
    return 1.0 + (risk_fraction * reward_to_risk_ratio)


def loss_multiplier(risk_fraction: float) -> float:
    return 1.0 - risk_fraction


def expected_log_growth_per_trial(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
) -> float:
    loss_rate = 1.0 - win_rate

    return win_rate * math.log(
        win_multiplier(risk_fraction, reward_to_risk_ratio)
    ) + loss_rate * math.log(loss_multiplier(risk_fraction))


def expected_terminal_bankroll(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
    trials: int,
    initial_bankroll: float,
) -> float:
    expected_multiplier_per_trial = 1.0 + expected_return_per_trial(
        win_rate=win_rate,
        reward_to_risk_ratio=reward_to_risk_ratio,
        risk_fraction=risk_fraction,
    )

    return initial_bankroll * (expected_multiplier_per_trial**trials)
