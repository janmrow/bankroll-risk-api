def edge_per_risk_unit(win_rate: float, reward_to_risk_ratio: float) -> float:
    loss_rate = 1.0 - win_rate
    return (win_rate * reward_to_risk_ratio) - loss_rate


def break_even_win_rate(reward_to_risk_ratio: float) -> float:
    return 1.0 / (1.0 + reward_to_risk_ratio)


def expected_return_per_trial(
    win_rate: float,
    reward_to_risk_ratio: float,
    risk_fraction: float,
) -> float:
    return risk_fraction * edge_per_risk_unit(win_rate, reward_to_risk_ratio)
