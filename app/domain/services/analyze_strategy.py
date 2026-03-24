from app.api.schemas.request import RiskAnalysisRequest
from app.api.schemas.response import (
    AnalysisInputs,
    AnalysisMetrics,
    AnalysisOutcomes,
    RiskAnalysisResponse,
    TerminalBankrollQuantiles,
)
from app.domain.assumptions import analysis_assumptions
from app.domain.formulas import (
    break_even_win_rate,
    edge_per_risk_unit,
    expected_log_growth_per_trial,
    expected_return_per_trial,
    expected_terminal_bankroll,
    half_kelly_fraction,
    horizon_ruin_probability,
    kelly_fraction,
    ruin_threshold_bankroll,
    terminal_bankroll_distribution,
    terminal_bankroll_quantiles,
)
from app.domain.warnings import build_warnings


def analyze_strategy(request: RiskAnalysisRequest) -> RiskAnalysisResponse:
    edge = edge_per_risk_unit(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
    )
    break_even = break_even_win_rate(request.reward_to_risk_ratio)
    expected_return = expected_return_per_trial(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
        risk_fraction=request.risk_fraction,
    )
    expected_log_growth = expected_log_growth_per_trial(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
        risk_fraction=request.risk_fraction,
    )
    kelly = kelly_fraction(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
    )
    half_kelly = half_kelly_fraction(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
    )

    expected_terminal = expected_terminal_bankroll(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
        risk_fraction=request.risk_fraction,
        trials=request.trials,
        initial_bankroll=request.initial_bankroll,
    )

    # PERFORMANCE: Pre-compute the full terminal binomial distribution exactly once (O(n)).
    # This prevents redundant heavy math operations (e.g. lgamma) across downstream metrics.
    bankrolls, probabilities = terminal_bankroll_distribution(
        win_rate=request.win_rate,
        reward_to_risk_ratio=request.reward_to_risk_ratio,
        risk_fraction=request.risk_fraction,
        trials=request.trials,
        initial_bankroll=request.initial_bankroll,
    )

    quantiles = terminal_bankroll_quantiles(
        bankrolls=bankrolls,
        probabilities=probabilities,
    )
    ruin_threshold = ruin_threshold_bankroll(
        initial_bankroll=request.initial_bankroll,
        ruin_threshold_fraction=request.ruin_threshold_fraction,
    )
    ruin_probability = horizon_ruin_probability(
        bankrolls=bankrolls,
        probabilities=probabilities,
        initial_bankroll=request.initial_bankroll,
        ruin_threshold_fraction=request.ruin_threshold_fraction,
    )

    return RiskAnalysisResponse(
        inputs=AnalysisInputs(**request.model_dump()),
        metrics=AnalysisMetrics(
            edge_per_risk_unit=edge,
            break_even_win_rate=break_even,
            expected_return_per_trial=expected_return,
            expected_log_growth_per_trial=expected_log_growth,
            kelly_fraction=kelly,
            half_kelly_fraction=half_kelly,
        ),
        outcomes=AnalysisOutcomes(
            expected_terminal_bankroll=expected_terminal,
            terminal_bankroll_quantiles=TerminalBankrollQuantiles(**quantiles),
            ruin_threshold_bankroll=ruin_threshold,
            horizon_ruin_probability=ruin_probability,
        ),
        warnings=build_warnings(
            edge_per_risk_unit=edge,
            expected_log_growth_per_trial=expected_log_growth,
            risk_fraction=request.risk_fraction,
            kelly_fraction=kelly,
            half_kelly_fraction=half_kelly,
        ),
        assumptions=analysis_assumptions(),
    )
