# Bankroll Risk API

Small, deterministic API for exact fixed-fraction bankroll risk analysis under repeated independent binary trials.

This project models a strategy with:

- constant win rate
- constant reward-to-risk ratio
- fixed fractional risk sizing
- independent trials
- binary outcomes

It is intentionally narrow in scope.

## What this project does

For a given strategy configuration, the API computes exact analytical metrics such as:

- edge per risk unit
- break-even win rate
- expected return per trial
- expected log growth per trial
- Kelly fraction
- half-Kelly fraction
- expected terminal bankroll
- terminal bankroll quantiles
- terminal horizon ruin probability

The model is based on a closed-form binomial distribution of terminal outcomes.

## What this project does not do

This project does not include:

- Monte Carlo simulation
- pathwise drawdown analysis
- first-passage / time-to-ruin models
- changing market regimes
- fees, slippage, taxes
- partial exits
- strategy comparison platform features
- database, auth, UI, CRUD

## Model

Definitions:

- `p = win_rate`
- `q = 1 - p`
- `R = reward_to_risk_ratio`
- `f = risk_fraction`
- `n = trials`
- `B0 = initial_bankroll`

Single-trial multipliers:

- win: `1 + fR`
- loss: `1 - f`

Terminal bankroll after `k` wins:

```text
B_n(k) = B0 * (1 + fR)^k * (1 - f)^(n-k)
```

Number of wins:

```text
k ~ Binomial(n, p)
```

### Ruin definition in V1

In this project, ruin means only:

```text
P(B_n <= ruin_threshold_fraction * initial_bankroll)
```

This is a terminal-horizon threshold probability.

It is not pathwise ruin.

## API

### Health endpoint

```http
GET /health
```

### Risk analysis endpoint

```http
POST /v1/risk/analyze
```

Example request:

```json
{
  "win_rate": 0.55,
  "reward_to_risk_ratio": 1.2,
  "risk_fraction": 0.02,
  "trials": 300,
  "initial_bankroll": 10000,
  "ruin_threshold_fraction": 0.25
}
```

Example response:

```json
{
  "model_version": "v1",
  "analysis_type": "exact_terminal_binomial",
  "inputs": {
    "win_rate": 0.55,
    "reward_to_risk_ratio": 1.2,
    "risk_fraction": 0.02,
    "trials": 300,
    "initial_bankroll": 10000.0,
    "ruin_threshold_fraction": 0.25
  },
  "metrics": {
    "edge_per_risk_unit": 0.21000000000000008,
    "break_even_win_rate": 0.45454545454545453,
    "expected_return_per_trial": 0.0042000000000000015,
    "expected_log_growth_per_trial": 0.003952871346640078,
    "kelly_fraction": 0.17500000000000004,
    "half_kelly_fraction": 0.08750000000000002
  },
  "outcomes": {
    "expected_terminal_bankroll": 35161.3152096248,
    "terminal_bankroll_quantiles": {
      "p05": 17700.222708440087,
      "p50": 32735.05417951463,
      "p95": 60540.694305772195
    },
    "ruin_threshold_bankroll": 2500.0,
    "horizon_ruin_probability": 5.705327450936433e-12
  },
  "warnings": [],
  "assumptions": [
    "independent_trials",
    "constant_win_rate",
    "constant_reward_to_risk_ratio",
    "fixed_fractional_risk_sizing",
    "binary_outcome_model",
    "no_fees_slippage_taxes_partial_exits_or_regime_changes"
  ]
}
```

## Warnings

The API may emit a small set of warnings:

- `negative_edge`
- `negative_expected_log_growth`
- `risk_fraction_above_kelly`
- `risk_fraction_above_half_kelly`

These are simple analytical flags, not a strategy scoring system.

## Request validation

Input validation is explicit and conservative:

- `0 <= win_rate <= 1`
- `reward_to_risk_ratio > 0`
- `0 <= risk_fraction < 1`
- `trials > 0`
- `initial_bankroll > 0`
- `0 <= ruin_threshold_fraction <= 1`

Unknown request fields are rejected.

## Project structure

```text
app/
  api/
    routes/
      risk.py
    schemas/
      request.py
      response.py
  domain/
    formulas/
      expectancy.py
      growth.py
      kelly.py
      terminal_distribution.py
    services/
      analyze_strategy.py
    warnings.py
    assumptions.py
  core/
    logging.py
    settings.py
  main.py

tests/
  unit/
  property/
  integration/
  contract/
```

## Tech stack

- Python 3.12
- FastAPI
- Pydantic v2
- NumPy
- pytest
- Hypothesis
- Ruff
- mypy
- Docker
- GitHub Actions
- uv

## Local development

### 1. Create environment and install dependencies

```bash
uv venv --python 3.12
uv sync --dev
```

### 2. Run the API

```bash
uv run uvicorn app.main:app --reload
```

App will be available at:

```text
http://127.0.0.1:8000
```

### 3. Quick manual checks

Health:

```bash
curl http://127.0.0.1:8000/health
```

Risk analysis:

```bash
curl -X POST http://127.0.0.1:8000/v1/risk/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "win_rate": 0.55,
    "reward_to_risk_ratio": 1.2,
    "risk_fraction": 0.02,
    "trials": 300,
    "initial_bankroll": 10000,
    "ruin_threshold_fraction": 0.25
  }'
```

## Testing

Run all checks:

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

Run test layers separately:

```bash
uv run pytest tests/unit
uv run pytest tests/property
uv run pytest tests/integration
uv run pytest tests/contract
```

## Docker

Build image:

```bash
docker build -t bankroll-risk-api .
```

Run container:

```bash
docker run --rm -p 8000:8000 bankroll-risk-api
```

Smoke check:

```bash
curl http://127.0.0.1:8000/health
```

## CI

GitHub Actions pipeline runs:

- Ruff
- mypy
- pytest
- Docker build
- container smoke test against `/health`

## Notes on numerical approach

The terminal outcome model is exact with respect to the binomial formulation used here.

A few implementation details are purely numerical safeguards:

- binomial probabilities are computed in log space for stability
- the probability mass function is normalized after computation to remove tiny floating-point drift
- terminal quantiles are taken from the discrete cumulative distribution using the left quantile convention

These choices do not change the analytical model.

## Why this project exists

This is a small portfolio project meant to show:

- clean API design
- disciplined scope control
- separation of HTTP and domain logic
- deterministic analytical modeling
- pragmatic QA/SDET thinking through unit, property, integration, and contract tests

It is deliberately small, closed, and engineering-first.
