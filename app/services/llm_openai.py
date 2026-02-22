from __future__ import annotations

import json
import logging
import math
from typing import Any

from openai import OpenAI

from app.core.settings import settings
from app.models.schemas import ReviewResponse
from app.services.reviewer import RUBRIC

logger = logging.getLogger(__name__)

_RUBRIC_TABLE = "\n".join(
    f"- {r['criterion']} (max {r['weight']} pts)" for r in RUBRIC
)

SYSTEM_PROMPT = f"""\
You are a VP Product reviewing a PRD for board-readiness. Given a PRD in Markdown, \
produce a structured JSON review that follows the provided JSON schema exactly. \
Be specific, actionable, and concise. Do not wrap the JSON in markdown code fences.

You MUST score the PRD using the following fixed rubric. Each criterion has a maximum \
weight; your score for each criterion must be between 0 and its weight (inclusive). \
The overall_score MUST equal the sum of all criterion scores.

Scoring rubric:
{_RUBRIC_TABLE}

In decision_trace.scoring_rubric, include exactly one entry per criterion above with \
fields: criterion, weight, score, notes. The "notes" field must focus on business \
consequences — explain impact on delivery risk, strategic alignment, or measurable \
outcomes. Avoid generic phrases like "missing" or "lacks detail".

In decision_trace, also include:

1. impact_profile — an object with three fields, each "low", "medium", or "high":
   - delivery_risk: based on scope clarity and risk coverage
   - strategic_alignment: based on problem, user, and solution coherence
   - measurement_maturity: based on metrics and experimentation readiness

2. readiness_level — one of: "Draft", "Pre-Discovery", "Validation Ready", \
"Build Ready", "Board Ready" — based on overall_score:
   - 0-24: Draft
   - 25-44: Pre-Discovery
   - 45-64: Validation Ready
   - 65-79: Build Ready
   - 80-100: Board Ready"""


def _build_user_prompt(prd_markdown: str, product_context: dict | None, audience: str | None) -> str:
    parts = [f"# PRD\n\n{prd_markdown}"]
    if product_context:
        parts.append(f"\n\n# Product Context\n\n{json.dumps(product_context, indent=2)}")
    if audience:
        parts.append(f"\n\n# Audience\n\n{audience}")
    parts.append("\n\nRespond with ONLY valid JSON matching the ReviewResponse schema.")
    return "".join(parts)


def _recompute_derived_fields(data: dict[str, Any]) -> None:
    """Enforce consistency of computed fields after LLM output."""
    trace = data.get("decision_trace", {})
    rubric = trace.get("scoring_rubric", [])

    computed_total = sum(item.get("score", 0) for item in rubric)
    data["overall_score"] = computed_total

    # Recompute confidence from score variance
    if rubric:
        ratios = [item["score"] / item["weight"] for item in rubric if item.get("weight", 0) > 0]
        if ratios:
            mean = sum(ratios) / len(ratios)
            variance = sum((r - mean) ** 2 for r in ratios) / len(ratios)
            std_dev = math.sqrt(variance)
            trace["confidence"] = max(0, min(100, int(round(30 + mean * 60 - std_dev * 80))))

    # Enforce readiness_level from overall_score
    score = data["overall_score"]
    if score >= 80:
        trace["readiness_level"] = "Board Ready"
    elif score >= 65:
        trace["readiness_level"] = "Build Ready"
    elif score >= 45:
        trace["readiness_level"] = "Validation Ready"
    elif score >= 25:
        trace["readiness_level"] = "Pre-Discovery"
    else:
        trace["readiness_level"] = "Draft"


def call_openai(prd_markdown: str, product_context: dict | None, audience: str | None) -> dict[str, Any]:
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(prd_markdown, product_context, audience),
            },
        ],
    )

    raw = response.choices[0].message.content
    if raw is None:
        raise RuntimeError("OpenAI returned an empty response")

    data: dict[str, Any] = json.loads(raw)
    _recompute_derived_fields(data)

    ReviewResponse.model_validate(data)
    return data
