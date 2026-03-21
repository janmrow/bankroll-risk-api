ASSUMPTIONS: tuple[str, ...] = (
    "independent_trials",
    "constant_win_rate",
    "constant_reward_to_risk_ratio",
    "fixed_fractional_risk_sizing",
    "binary_outcome_model",
    "no_fees_slippage_taxes_partial_exits_or_regime_changes",
)


def analysis_assumptions() -> list[str]:
    return list(ASSUMPTIONS)
