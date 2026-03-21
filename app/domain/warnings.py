def build_warnings(
    edge_per_risk_unit: float,
    expected_log_growth_per_trial: float,
    risk_fraction: float,
    kelly_fraction: float,
    half_kelly_fraction: float,
) -> list[str]:
    warnings: list[str] = []

    if edge_per_risk_unit < 0.0:
        warnings.append("negative_edge")

    if expected_log_growth_per_trial < 0.0:
        warnings.append("negative_expected_log_growth")

    if risk_fraction > kelly_fraction:
        warnings.append("risk_fraction_above_kelly")

    if risk_fraction > half_kelly_fraction:
        warnings.append("risk_fraction_above_half_kelly")

    return warnings
