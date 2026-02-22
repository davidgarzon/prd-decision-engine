import copy

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ReviewResponse
from app.services.reviewer import RUBRIC

client = TestClient(app)

SAMPLE_PAYLOAD = {
    "prd_markdown": "# My Product\n\nThis is a sample PRD for testing.",
    "product_context": {"domain": "fintech", "stage": "early"},
    "audience": "engineering leadership",
    "mode": "mock",
}

RICH_PRD_PAYLOAD = {
    "prd_markdown": (
        "# Widget Optimizer\n\n"
        "## Problem\nUsers struggle with a painful inefficiency in their workflow.\n\n"
        "## User Personas\nPersona: Maria, a small-business customer and end-user.\n\n"
        "## Scope\nMVP includes phase 1 deliverables. Out of scope: advanced analytics.\n\n"
        "## Success Metrics\nKPI: activation rate target 60%, baseline 40%, conversion metric.\n\n"
        "## Risks & Dependencies\nRisk: vendor dependency. Mitigation: adapter layer. Compliance required.\n\n"
        "## Solution Architecture\nAPI endpoint, component design, system flow diagram.\n\n"
        "## Rollout\nPhased rollout with A/B experiment, beta launch, feature flag, canary deploy.\n"
    ),
    "mode": "mock",
}

SPARSE_PAYLOAD = {
    "prd_markdown": "# Idea\n\nJust a vague idea with no detail whatsoever.",
    "mode": "mock",
}

EXPECTED_CRITERIA = [r["criterion"] for r in RUBRIC]
VALID_RISK_LEVELS = {"low", "medium", "high"}
VALID_READINESS_LEVELS = {"Draft", "Pre-Discovery", "Validation Ready", "Build Ready", "Board Ready"}


# ── Basic endpoint tests ─────────────────────────────────────────────────────


def test_review_mock_returns_200():
    resp = client.post("/review", json=SAMPLE_PAYLOAD)
    assert resp.status_code == 200
    ReviewResponse.model_validate(resp.json())


def test_review_score_in_range():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    assert 0 <= data["overall_score"] <= 100


def test_review_list_max_lengths():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    assert len(data["strengths"]) <= 6
    assert len(data["gaps"]) <= 10
    assert len(data["risks"]) <= 8
    assert len(data["questions"]) <= 12
    assert len(data["metrics"]) <= 8
    assert len(data["suggested_experiments"]) <= 5


def test_review_deterministic():
    resp1 = client.post("/review", json=SAMPLE_PAYLOAD).json()
    resp2 = client.post("/review", json=SAMPLE_PAYLOAD).json()
    assert resp1 == resp2


def test_review_different_input_gives_different_output():
    payload2 = copy.deepcopy(SAMPLE_PAYLOAD)
    payload2["prd_markdown"] = "# Another PRD\n\nCompletely different content."
    resp1 = client.post("/review", json=SAMPLE_PAYLOAD).json()
    resp2 = client.post("/review", json=payload2).json()
    assert resp1 != resp2


def test_review_missing_prd_returns_422():
    resp = client.post("/review", json={"mode": "mock"})
    assert resp.status_code == 422


def test_review_auto_mode_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core import settings as settings_mod

    monkeypatch.setattr(settings_mod.settings, "openai_api_key", None)

    payload = copy.deepcopy(SAMPLE_PAYLOAD)
    payload["mode"] = "auto"
    resp = client.post("/review", json=payload)
    assert resp.status_code == 200


def test_schema_endpoint():
    resp = client.get("/schema")
    assert resp.status_code == 200
    schema = resp.json()
    assert "properties" in schema
    assert "overall_score" in schema["properties"]


# ── Rubric structure tests ───────────────────────────────────────────────────


def test_rubric_has_7_criteria():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    rubric = data["decision_trace"]["scoring_rubric"]
    assert len(rubric) == 7


def test_rubric_criteria_names_match():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    criteria = [item["criterion"] for item in data["decision_trace"]["scoring_rubric"]]
    assert criteria == EXPECTED_CRITERIA


def test_rubric_weights_sum_to_100():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    total_weight = sum(item["weight"] for item in data["decision_trace"]["scoring_rubric"])
    assert total_weight == 100


def test_rubric_scores_do_not_exceed_weights():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    for item in data["decision_trace"]["scoring_rubric"]:
        assert 0 <= item["score"] <= item["weight"], (
            f"{item['criterion']}: score {item['score']} exceeds weight {item['weight']}"
        )


def test_overall_score_equals_rubric_sum():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    rubric_sum = sum(item["score"] for item in data["decision_trace"]["scoring_rubric"])
    assert data["overall_score"] == rubric_sum


def test_sparse_prd_scores_low_on_missing_areas():
    data = client.post("/review", json=SPARSE_PAYLOAD).json()
    rubric = {item["criterion"]: item for item in data["decision_trace"]["scoring_rubric"]}
    assert rubric["Success Metrics"]["score"] <= 5
    assert rubric["Risks & Dependencies"]["score"] <= 5
    assert rubric["User Definition"]["score"] <= 5


def test_rich_prd_scores_higher():
    data = client.post("/review", json=RICH_PRD_PAYLOAD).json()
    sparse_data = client.post(
        "/review",
        json={"prd_markdown": "# Bare idea\n\nNothing here.", "mode": "mock"},
    ).json()
    assert data["overall_score"] > sparse_data["overall_score"]


# ── Notes quality tests ──────────────────────────────────────────────────────


def test_notes_mention_business_consequences():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    for item in data["decision_trace"]["scoring_rubric"]:
        note = item["notes"].lower()
        assert "missing" not in note.split(), (
            f"{item['criterion']}: note should not use generic 'missing'"
        )
        assert len(item["notes"]) > 40, (
            f"{item['criterion']}: note too short to convey business impact"
        )


# ── Impact profile tests ────────────────────────────────────────────────────


def test_impact_profile_present():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    profile = data["decision_trace"]["impact_profile"]
    assert "delivery_risk" in profile
    assert "strategic_alignment" in profile
    assert "measurement_maturity" in profile


def test_impact_profile_valid_values():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    profile = data["decision_trace"]["impact_profile"]
    assert profile["delivery_risk"] in VALID_RISK_LEVELS
    assert profile["strategic_alignment"] in VALID_RISK_LEVELS
    assert profile["measurement_maturity"] in VALID_RISK_LEVELS


def test_impact_profile_deterministic():
    d1 = client.post("/review", json=SAMPLE_PAYLOAD).json()["decision_trace"]["impact_profile"]
    d2 = client.post("/review", json=SAMPLE_PAYLOAD).json()["decision_trace"]["impact_profile"]
    assert d1 == d2


def test_rich_prd_has_lower_delivery_risk():
    rich = client.post("/review", json=RICH_PRD_PAYLOAD).json()
    sparse = client.post("/review", json=SPARSE_PAYLOAD).json()
    risk_order = {"low": 0, "medium": 1, "high": 2}
    rich_risk = risk_order[rich["decision_trace"]["impact_profile"]["delivery_risk"]]
    sparse_risk = risk_order[sparse["decision_trace"]["impact_profile"]["delivery_risk"]]
    assert rich_risk <= sparse_risk


def test_measurement_maturity_low_when_no_rollout():
    payload = {
        "prd_markdown": (
            "# Metrics-only PRD\n\n"
            "## Success Metrics\n"
            "KPI: activation rate target 60%, baseline 40%, conversion metric, "
            "retention north star OKR measurement.\n"
        ),
        "mode": "mock",
    }
    data = client.post("/review", json=payload).json()
    rubric = {item["criterion"]: item for item in data["decision_trace"]["scoring_rubric"]}
    assert rubric["Rollout & Experimentation"]["score"] < 5
    assert data["decision_trace"]["impact_profile"]["measurement_maturity"] == "low"


# ── Readiness level tests ───────────────────────────────────────────────────


def test_readiness_level_present():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    assert data["decision_trace"]["readiness_level"] in VALID_READINESS_LEVELS


def test_readiness_level_consistent_with_score():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    score = data["overall_score"]
    level = data["decision_trace"]["readiness_level"]
    if score >= 80:
        assert level == "Board Ready"
    elif score >= 65:
        assert level == "Build Ready"
    elif score >= 45:
        assert level == "Validation Ready"
    elif score >= 25:
        assert level == "Pre-Discovery"
    else:
        assert level == "Draft"


def test_sparse_prd_readiness_is_low():
    data = client.post("/review", json=SPARSE_PAYLOAD).json()
    assert data["decision_trace"]["readiness_level"] in {"Draft", "Pre-Discovery"}


# ── Confidence tests ─────────────────────────────────────────────────────────


def test_confidence_in_range():
    data = client.post("/review", json=SAMPLE_PAYLOAD).json()
    assert 0 <= data["decision_trace"]["confidence"] <= 100


def test_confidence_deterministic():
    c1 = client.post("/review", json=SAMPLE_PAYLOAD).json()["decision_trace"]["confidence"]
    c2 = client.post("/review", json=SAMPLE_PAYLOAD).json()["decision_trace"]["confidence"]
    assert c1 == c2


def test_rich_prd_has_higher_confidence_than_sparse():
    rich = client.post("/review", json=RICH_PRD_PAYLOAD).json()
    sparse = client.post("/review", json=SPARSE_PAYLOAD).json()
    assert rich["decision_trace"]["confidence"] >= sparse["decision_trace"]["confidence"]
