def kelly_fraction(win_rate: float, reward_to_risk_ratio: float) -> float:
    loss_rate = 1.0 - win_rate
    raw_fraction = win_rate - (loss_rate / reward_to_risk_ratio)
    return max(0.0, raw_fraction)


def half_kelly_fraction(win_rate: float, reward_to_risk_ratio: float) -> float:
    return 0.5 * kelly_fraction(win_rate, reward_to_risk_ratio)
