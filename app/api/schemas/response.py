from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResponseBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalysisInputs(ResponseBaseModel):
    win_rate: float
    reward_to_risk_ratio: float
    risk_fraction: float
    trials: int
    initial_bankroll: float
    ruin_threshold_fraction: float


class AnalysisMetrics(ResponseBaseModel):
    edge_per_risk_unit: float
    break_even_win_rate: float
    expected_return_per_trial: float
    expected_log_growth_per_trial: float
    kelly_fraction: float
    half_kelly_fraction: float


class TerminalBankrollQuantiles(ResponseBaseModel):
    p05: float
    p50: float
    p95: float


class AnalysisOutcomes(ResponseBaseModel):
    expected_terminal_bankroll: float
    terminal_bankroll_quantiles: TerminalBankrollQuantiles
    ruin_threshold_bankroll: float
    horizon_ruin_probability: float


class RiskAnalysisResponse(ResponseBaseModel):
    model_version: Literal["v1"] = Field(default="v1")
    analysis_type: Literal["exact_terminal_binomial"] = Field(
        default="exact_terminal_binomial"
    )
    inputs: AnalysisInputs
    metrics: AnalysisMetrics
    outcomes: AnalysisOutcomes
    warnings: list[str]
    assumptions: list[str]
