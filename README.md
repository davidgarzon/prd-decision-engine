![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063)
![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen)

# prd-decision-engine

A structured decision engine for evaluating Product Requirements Documents. It scores PRDs against a weighted rubric, surfaces delivery risks, gauges measurement maturity, and assigns a readiness level — giving product leaders an objective, reproducible signal on whether a document is ready for the next stage of investment.

Works out of the box in **mock mode** (no API key needed) and optionally calls **OpenAI** for real LLM-powered analysis.

## Use Cases

- **CPO / VP Product** — Run every PRD through the engine before a board review to catch blind spots and quantify readiness.
- **Product Managers** — Get instant feedback on draft PRDs during writing; iterate until the score reaches "Build Ready" or above.
- **Cross-functional teams** — Use the impact profile and rubric breakdown as a shared language for prioritization and sprint planning.

## Quickstart

```bash
# 1. Clone & enter the repo
git clone <repo-url> && cd prd-decision-engine

# 2. Create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure OpenAI
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 5. Start the server
python -m uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/review` | Submit a PRD for review |
| `GET` | `/schema` | JSON Schema of the review response |

## Example Output (excerpt)

```json
{
  "overall_score": 72,
  "decision_trace": {
    "readiness_level": "Build Ready",
    "impact_profile": {
      "delivery_risk": "medium",
      "strategic_alignment": "high",
      "measurement_maturity": "medium"
    },
    "scoring_rubric": [
      {
        "criterion": "Problem Clarity",
        "weight": 20,
        "score": 17,
        "notes": "The problem is grounded in quantified user pain and market evidence, giving stakeholders confidence that engineering investment addresses a validated need"
      }
    ],
    "confidence": 68
  }
}
```

## Demo

Start the server, then in another terminal:

```bash
chmod +x examples/run_demo.sh
./examples/run_demo.sh
```

Or call the API directly:

```bash
# Health check
curl http://127.0.0.1:8000/health

# Submit a review (mock mode, no API key required)
curl -s -X POST http://127.0.0.1:8000/review \
  -H "Content-Type: application/json" \
  -d @examples/review_request.json | python3 -m json.tool
```

## Running Tests

```bash
pytest -v
```

All tests run in mock mode and do not require an API key.

## Mode Behavior

| `mode` field | `OPENAI_API_KEY` set? | Behavior |
|--------------|-----------------------|----------|
| `"mock"` | any | Deterministic mock review |
| `"auto"` | yes | OpenAI LLM review |
| `"auto"` | no | Falls back to mock |
| omitted | yes | OpenAI LLM review |
| omitted | no | Falls back to mock |

## How Scoring Works

### Weighted Rubric (100 points)

Every PRD is evaluated against a fixed rubric with **7 criteria**. Each criterion receives a score between **0** and its **weight**, and the `overall_score` is the **sum of all criterion scores** (0–100).

| Criterion | Weight | What it evaluates |
|-----------|--------|-------------------|
| Problem Clarity | 20 | Is the problem grounded in quantified user pain and market evidence? |
| User Definition | 15 | Are target users, personas, or segments clearly identified? |
| Scope Definition | 15 | Is there an explicit MVP boundary with phased delivery? |
| Success Metrics | 15 | Are KPIs quantified with baselines, targets, and measurement plans? |
| Risks & Dependencies | 15 | Are risks identified with mitigations and dependencies mapped? |
| Solution Coherence | 10 | Is the technical approach logically structured and buildable? |
| Rollout & Experimentation | 10 | Is there a phased rollout or hypothesis-driven experiment plan? |

In **mock mode**, scores come from keyword-based heuristics (e.g., no metrics-related terms → Success Metrics ≤ 5). In **LLM mode**, the model evaluates each criterion explicitly. Notes focus on business consequences — delivery risk, strategic alignment, and measurable outcomes — rather than generic observations.

### Impact Profile

The `decision_trace.impact_profile` provides a qualitative risk assessment derived from the rubric scores:

| Dimension | Derived from | Meaning |
|-----------|-------------|---------|
| `delivery_risk` | Scope Definition + Risks & Dependencies | Likelihood of timeline/budget overrun |
| `strategic_alignment` | Problem Clarity + User Definition + Solution Coherence | How well the initiative maps to validated need |
| `measurement_maturity` | Success Metrics + Rollout & Experimentation | Ability to objectively measure outcomes |

Each dimension is rated **low**, **medium**, or **high**. Notably, `measurement_maturity` is forced to **low** whenever Rollout & Experimentation scores below 5 — strong metrics without a delivery plan to validate them do not constitute measurement readiness.

### Readiness Level

Based on the `overall_score`, every review includes a `readiness_level`:

| Score Range | Readiness Level |
|-------------|----------------|
| 0 – 24 | Draft |
| 25 – 44 | Pre-Discovery |
| 45 – 64 | Validation Ready |
| 65 – 79 | Build Ready |
| 80 – 100 | Board Ready |

### Confidence

The `confidence` score (0–100) reflects how **reliable** the overall assessment is. It is computed from two factors:

1. **Completeness** — higher average criterion scores → higher confidence.
2. **Variance** — large differences between criterion scores → lower confidence (an uneven PRD is harder to judge holistically).

The full breakdown is always available in `decision_trace`.

## Project Structure

```
app/
  main.py              # FastAPI application entrypoint
  api/routes.py        # Route definitions
  core/settings.py     # Configuration via pydantic-settings
  models/schemas.py    # Pydantic v2 request/response models
  services/
    reviewer.py        # Orchestrator: picks mock vs LLM
    llm_openai.py      # OpenAI adapter
tests/
  test_health.py       # Health endpoint tests
  test_review.py       # Review endpoint tests
examples/
  prd_sample.md        # Sample PRD document
  review_request.json  # Sample request payload
  run_demo.sh          # End-to-end demo script
```
