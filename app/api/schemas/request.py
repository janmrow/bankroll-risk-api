import math

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "win_rate": 0.55,
                "reward_to_risk_ratio": 1.2,
                "risk_fraction": 0.02,
                "trials": 300,
                "initial_bankroll": 10000,
                "ruin_threshold_fraction": 0.25,
            }
        },
    )

    win_rate: float = Field(ge=0.0, le=1.0)

    # Sanity bound for extreme payouts
    reward_to_risk_ratio: float = Field(gt=0.0, le=1000.0)

    risk_fraction: float = Field(ge=0.0, lt=1.0)

    # Resource protection: prevents excessive memory allocation in simulation
    trials: int = Field(gt=0, le=10000)

    # Numerical stability: prevents infinity during bankroll calculations
    initial_bankroll: float = Field(gt=0.0, le=1_000_000_000_000.0)

    ruin_threshold_fraction: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def prevent_float_overflow(self) -> "RiskAnalysisRequest":
        win_multiplier = 1.0 + (self.risk_fraction * self.reward_to_risk_ratio)

        if win_multiplier > 1.0:
            # Use log10 to prevent float64 overflow (~10^308)
            # Cap at 10^250 to provide a safe computation margin
            if self.trials * math.log10(win_multiplier) > 250:
                raise ValueError("Inputs result in values too large for exact float precision")
        return self
