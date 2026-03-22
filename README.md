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

*(See OpenAPI schema at `/openapi.json` for full response structure and metrics).*

## Request validation & Safety

Input validation is explicit and mathematically conservative:

- `0 <= win_rate <= 1`
- `0 < reward_to_risk_ratio <= 1000`
- `0 <= risk_fraction < 1`
- `0 < trials <= 10000`
- `0 < initial_bankroll <= 1_000_000_000_000`
- `0 <= ruin_threshold_fraction <= 1`

**Float Overflow Protection:** The API employs a logarithmic evaluation step (`O(1)`) in the Pydantic validator before processing. If inputs would result in a mathematically valid but computationally impossible value (exceeding IEEE 754 float64 limits, `~10^308`), it safely rejects the request with a `422 Unprocessable Entity` instead of allowing a `500 Internal Server Error`.

## Tech stack

- **Core:** Python 3.12, FastAPI, Pydantic v2, NumPy
- **QA/SDET:** pytest, Hypothesis, Schemathesis, mutmut
- **Tooling:** Ruff, mypy, uv, Docker, GitHub Actions

## Testing Strategy (QA/SDET Showcase)

This project implements a multi-layered, aggressive testing strategy designed to protect exact analytical formulas:

1. **Unit & Integration:** Standard exact-value verification and HTTP routing checks.
2. **Property-Based Testing (`Hypothesis`):** Verifies mathematical invariants (e.g., ruin probabilities must stay within `[0, 1]`, higher win rates must not increase ruin probability).
3. **Contract & Fuzzing (`Schemathesis`):** Automatically reads the OpenAPI schema and bombs the endpoints with extreme inputs to prove zero unhandled exceptions (no 5xx errors) and strict Pydantic response compliance.
4. **Mutation Testing (`mutmut`):** Achieves a **100% mutation kill rate**. Any change to the domain logic (flipped operators, off-by-one errors) is immediately caught by the test suite, proving the tests have true semantic understanding of the domain, not just high line coverage.

## Local development

### 1. Create environment and run API

```bash
uv venv --python 3.12
uv sync --dev
uv run uvicorn app.main:app --reload
```

### 2. Run test layers

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

Run advanced QA tooling:

```bash
# OpenAPI Fuzzing
uv run pytest tests/contract/test_fuzzing.py -v

# Mutation Testing
uv run mutmut run --paths-to-mutate app/domain/formulas/
uv run mutmut results
```

## Docker

Build image & run container:

```bash
docker build -t bankroll-risk-api .
docker run --rm -p 8000:8000 bankroll-risk-api
curl http://127.0.0.1:8000/health
```

## Why this project exists

This is a small portfolio project meant to show:

- clean API design and disciplined scope control
- strict separation of HTTP and domain logic
- deterministic analytical modeling over simulation
- advanced SDET methodologies (Property, Fuzzing, Mutation testing)

It is deliberately small, closed, and engineering-first.
