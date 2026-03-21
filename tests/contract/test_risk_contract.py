import math

from fastapi.testclient import TestClient

from app.main import app


def assert_no_nan_or_infinite(value: object) -> None:
    if isinstance(value, dict):
        for nested_value in value.values():
            assert_no_nan_or_infinite(nested_value)
        return

    if isinstance(value, list):
        for nested_value in value:
            assert_no_nan_or_infinite(nested_value)
        return

    if isinstance(value, (int, float)):
        assert math.isfinite(float(value))


def test_valid_request_returns_stable_response_contract() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/risk/analyze",
        json={
            "win_rate": 0.55,
            "reward_to_risk_ratio": 1.2,
            "risk_fraction": 0.02,
            "trials": 300,
            "initial_bankroll": 10_000,
            "ruin_threshold_fraction": 0.25,
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert set(payload.keys()) == {
        "model_version",
        "analysis_type",
        "inputs",
        "metrics",
        "outcomes",
        "warnings",
        "assumptions",
    }
    assert set(payload["inputs"].keys()) == {
        "win_rate",
        "reward_to_risk_ratio",
        "risk_fraction",
        "trials",
        "initial_bankroll",
        "ruin_threshold_fraction",
    }
    assert set(payload["metrics"].keys()) == {
        "edge_per_risk_unit",
        "break_even_win_rate",
        "expected_return_per_trial",
        "expected_log_growth_per_trial",
        "kelly_fraction",
        "half_kelly_fraction",
    }
    assert set(payload["outcomes"].keys()) == {
        "expected_terminal_bankroll",
        "terminal_bankroll_quantiles",
        "ruin_threshold_bankroll",
        "horizon_ruin_probability",
    }
    assert set(payload["outcomes"]["terminal_bankroll_quantiles"].keys()) == {
        "p05",
        "p50",
        "p95",
    }

    assert_no_nan_or_infinite(payload)


def test_invalid_request_returns_422() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/risk/analyze",
        json={
            "win_rate": 1.5,
            "reward_to_risk_ratio": 1.2,
            "risk_fraction": 0.02,
            "trials": 300,
            "initial_bankroll": 10_000,
            "ruin_threshold_fraction": 0.25,
        },
    )

    assert response.status_code == 422
