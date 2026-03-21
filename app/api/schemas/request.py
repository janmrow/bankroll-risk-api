from pydantic import BaseModel, ConfigDict, Field


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
    reward_to_risk_ratio: float = Field(gt=0.0)
    risk_fraction: float = Field(ge=0.0, lt=1.0)
    trials: int = Field(gt=0)
    initial_bankroll: float = Field(gt=0.0)
    ruin_threshold_fraction: float = Field(ge=0.0, le=1.0)
