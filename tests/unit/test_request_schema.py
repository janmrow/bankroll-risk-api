import pytest
from pydantic import ValidationError

from app.api.schemas.request import RiskAnalysisRequest


def valid_payload() -> dict[str, float | int]:
    return {
        "win_rate": 0.55,
        "reward_to_risk_ratio": 1.2,
        "risk_fraction": 0.02,
        "trials": 300,
        "initial_bankroll": 10_000,
        "ruin_threshold_fraction": 0.25,
    }


def test_request_schema_accepts_valid_payload() -> None:
    model = RiskAnalysisRequest.model_validate(valid_payload())

    assert model.win_rate == pytest.approx(0.55)
    assert model.trials == 300


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("win_rate", 1.1),
        ("reward_to_risk_ratio", 0.0),
        ("risk_fraction", 1.0),
        ("trials", 0),
        ("initial_bankroll", 0.0),
        ("ruin_threshold_fraction", -0.1),
    ],
)
def test_request_schema_rejects_invalid_inputs(
    field_name: str,
    field_value: float | int,
) -> None:
    payload = valid_payload()
    payload[field_name] = field_value

    with pytest.raises(ValidationError):
        RiskAnalysisRequest.model_validate(payload)


def test_request_schema_rejects_extra_fields() -> None:
    payload = valid_payload()
    payload["unexpected"] = 123

    with pytest.raises(ValidationError):
        RiskAnalysisRequest.model_validate(payload)
