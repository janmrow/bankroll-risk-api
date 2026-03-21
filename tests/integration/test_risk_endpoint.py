from fastapi.testclient import TestClient

from app.main import app


def test_risk_analyze_endpoint_returns_full_response() -> None:
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
    assert payload["model_version"] == "v1"
    assert payload["analysis_type"] == "exact_terminal_binomial"

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
