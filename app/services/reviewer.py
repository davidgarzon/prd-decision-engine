from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from typing import Any

from app.core.settings import settings
from app.models.schemas import ReviewRequest, ReviewResponse

logger = logging.getLogger(__name__)

# ── Fixed rubric definition ──────────────────────────────────────────────────

RUBRIC: list[dict[str, Any]] = [
    {"criterion": "Problem Clarity", "weight": 20},
    {"criterion": "User Definition", "weight": 15},
    {"criterion": "Scope Definition", "weight": 15},
    {"criterion": "Success Metrics", "weight": 15},
    {"criterion": "Risks & Dependencies", "weight": 15},
    {"criterion": "Solution Coherence", "weight": 10},
    {"criterion": "Rollout & Experimentation", "weight": 10},
]

# ── Keyword patterns for mock heuristic scoring ─────────────────────────────

_KW_PROBLEM = re.compile(
    r"problem|pain\s*point|challenge|issue|gap|frustrat|struggle|inefficien", re.I
)
_KW_USER = re.compile(
    r"user|persona|customer|segment|audience|stakeholder|buyer|end.?user", re.I
)
_KW_SCOPE = re.compile(
    r"scope|mvp|phase|milestone|out.of.scope|boundary|requirement|in.scope|deliverable", re.I
)
_KW_METRICS = re.compile(
    r"metric|kpi|success\s*criter|measur|target|baseline|north\s*star|okr|conversion|retention", re.I
)
_KW_RISKS = re.compile(
    r"risk|depend|mitiga|block|threat|vulnerab|complian|regulat|constraint", re.I
)
_KW_SOLUTION = re.compile(
    r"solution|architect|design|approach|flow|diagram|system|api|endpoint|component|module", re.I
)
_KW_ROLLOUT = re.compile(
    r"rollout|experiment|a/b|canary|beta|launch|pilot|feature.flag|gradual|phased|hypothesis", re.I
)

_PATTERNS = [_KW_PROBLEM, _KW_USER, _KW_SCOPE, _KW_METRICS, _KW_RISKS, _KW_SOLUTION, _KW_ROLLOUT]

# ── VP-quality notes: (high_score_note, low_score_note) ─────────────────────

_NOTES: dict[str, tuple[str, str]] = {
    "Problem Clarity": (
        "The problem is grounded in quantified user pain and market evidence, "
        "giving stakeholders confidence that engineering investment addresses a validated need",
        "Without a data-backed problem statement, the team risks building a solution "
        "in search of a problem — increasing the likelihood of post-launch pivot and wasted cycles",
    ),
    "User Definition": (
        "Well-segmented user profiles enable targeted go-to-market and reduce the risk of "
        "building features that satisfy no one by trying to serve everyone",
        "Ambiguous user definition undermines prioritization — engineering and design cannot "
        "make confident trade-offs without knowing whose outcomes drive business value",
    ),
    "Scope Definition": (
        "Explicit MVP boundaries and phased delivery protect the team from scope creep "
        "and give leadership clear checkpoints for go/no-go decisions",
        "Undefined scope creates unbounded delivery risk; teams tend to gold-plate without "
        "a hard cut-line, threatening both timeline and budget predictability",
    ),
    "Success Metrics": (
        "Quantified KPIs with baselines and targets enable objective launch decisions "
        "and make it possible to kill underperforming initiatives early",
        "Without measurable success criteria the organization cannot objectively evaluate ROI, "
        "making board-level investment decisions rely on anecdotes rather than evidence",
    ),
    "Risks & Dependencies": (
        "Proactive risk mapping with concrete mitigations demonstrates operational maturity "
        "and reduces the probability of delivery surprises that erode stakeholder trust",
        "Unacknowledged risks surface as firefighting during execution — each unmitigated "
        "dependency is a potential single point of failure for the entire initiative",
    ),
    "Solution Coherence": (
        "A logically structured technical approach signals that the proposed solution can actually "
        "be built within constraints, reducing integration risk downstream",
        "A loosely defined solution creates ambiguity in estimation and architecture, "
        "increasing the chance of costly mid-sprint redesigns",
    ),
    "Rollout & Experimentation": (
        "A phased rollout with hypothesis-driven experiments allows the team to validate "
        "assumptions incrementally and course-correct before full-scale commitment",
        "Launching without an experimentation plan means the first real feedback arrives at GA, "
        "when the cost of change is highest and reputational exposure is maximum",
    ),
}


def _stable_seed(request: ReviewRequest) -> int:
    payload = json.dumps(
        {
            "prd_markdown": request.prd_markdown,
            "product_context": request.product_context,
            "audience": request.audience,
        },
        sort_keys=True,
    )
    return int(hashlib.sha256(payload.encode()).hexdigest(), 16)


def _pick(seed: int, options: list[str], count: int) -> list[str]:
    rng = seed
    result: list[str] = []
    pool = list(options)
    for _ in range(min(count, len(pool))):
        rng = (rng * 6364136223846793005 + 1) & 0xFFFFFFFFFFFFFFFF
        idx = rng % len(pool)
        result.append(pool.pop(int(idx)))
    return result


def _keyword_score(pattern: re.Pattern[str], text: str, weight: int, seed: int) -> int:
    hits = len(pattern.findall(text))
    if hits == 0:
        return min(3, weight)
    if hits <= 2:
        base = int(weight * 0.4)
    elif hits <= 5:
        base = int(weight * 0.65)
    else:
        base = int(weight * 0.85)
    jitter = seed % 3
    return min(base + jitter, weight)


def _score_rubric_mock(prd: str, seed: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for rubric_entry, pattern in zip(RUBRIC, _PATTERNS):
        criterion = rubric_entry["criterion"]
        weight = rubric_entry["weight"]
        subseed = (seed >> 3) ^ hash(criterion)
        score = _keyword_score(pattern, prd, weight, subseed & 0xFFFFFFFF)
        good_note, bad_note = _NOTES[criterion]
        note = good_note if score > weight * 0.5 else bad_note
        items.append({"criterion": criterion, "weight": weight, "score": score, "notes": note})
    return items


# ── Impact profile & readiness ───────────────────────────────────────────────


def _tri_level(value: float, low_threshold: float, high_threshold: float) -> str:
    if value <= low_threshold:
        return "low"
    if value >= high_threshold:
        return "high"
    return "medium"


def _compute_impact_profile(rubric_items: list[dict[str, Any]]) -> dict[str, str]:
    by_name = {item["criterion"]: item for item in rubric_items}

    scope_pct = by_name["Scope Definition"]["score"] / by_name["Scope Definition"]["weight"]
    risk_pct = by_name["Risks & Dependencies"]["score"] / by_name["Risks & Dependencies"]["weight"]
    delivery_raw = 1.0 - (scope_pct * 0.5 + risk_pct * 0.5)
    delivery_risk = _tri_level(delivery_raw, 0.35, 0.65)

    problem_pct = by_name["Problem Clarity"]["score"] / by_name["Problem Clarity"]["weight"]
    user_pct = by_name["User Definition"]["score"] / by_name["User Definition"]["weight"]
    solution_pct = by_name["Solution Coherence"]["score"] / by_name["Solution Coherence"]["weight"]
    alignment_raw = problem_pct * 0.4 + user_pct * 0.3 + solution_pct * 0.3
    strategic_alignment = _tri_level(alignment_raw, 0.35, 0.6)

    rollout_score = by_name["Rollout & Experimentation"]["score"]
    metrics_pct = by_name["Success Metrics"]["score"] / by_name["Success Metrics"]["weight"]
    rollout_pct = rollout_score / by_name["Rollout & Experimentation"]["weight"]

    if rollout_score < 5:
        measurement_maturity = "low"
    else:
        measurement_raw = metrics_pct * 0.6 + rollout_pct * 0.4
        measurement_maturity = _tri_level(measurement_raw, 0.35, 0.6)

    return {
        "delivery_risk": delivery_risk,
        "strategic_alignment": strategic_alignment,
        "measurement_maturity": measurement_maturity,
    }


def _compute_readiness_level(overall_score: int) -> str:
    if overall_score >= 80:
        return "Board Ready"
    if overall_score >= 65:
        return "Build Ready"
    if overall_score >= 45:
        return "Validation Ready"
    if overall_score >= 25:
        return "Pre-Discovery"
    return "Draft"


# ── Confidence based on score variance ───────────────────────────────────────


def _compute_confidence(rubric_items: list[dict[str, Any]]) -> int:
    ratios = [item["score"] / item["weight"] for item in rubric_items]
    mean = sum(ratios) / len(ratios)
    variance = sum((r - mean) ** 2 for r in ratios) / len(ratios)
    std_dev = math.sqrt(variance)

    completeness_bonus = mean * 60
    variance_penalty = std_dev * 80

    confidence = int(round(30 + completeness_bonus - variance_penalty))
    return max(0, min(100, confidence))


# ── Mock review builder ──────────────────────────────────────────────────────


def _mock_review(request: ReviewRequest) -> dict[str, Any]:
    seed = _stable_seed(request)
    prd = request.prd_markdown

    rubric_items = _score_rubric_mock(prd, seed)
    overall_score = sum(item["score"] for item in rubric_items)

    strengths_pool = [
        "Clear problem statement",
        "Well-defined success metrics",
        "Strong competitive analysis",
        "Detailed user personas",
        "Realistic timeline",
        "Thorough risk assessment",
    ]
    strengths = _pick(seed, strengths_pool, 3)

    impact_profile = _compute_impact_profile(rubric_items)
    readiness_level = _compute_readiness_level(overall_score)
    confidence = _compute_confidence(rubric_items)

    return {
        "overall_score": overall_score,
        "summary": f"Mock review of PRD ({len(prd)} chars). "
        "The document covers the core idea but could benefit from more detail in several areas.",
        "strengths": strengths,
        "gaps": [
            {
                "area": "User Research",
                "why": "No user interviews or survey data referenced",
                "suggested_fix": "Include at least 5 user interviews or a survey with n>50",
            },
            {
                "area": "Technical Feasibility",
                "why": "Missing architecture diagram",
                "suggested_fix": "Add a high-level system architecture section",
            },
        ],
        "risks": [
            {
                "risk": "Scope creep",
                "impact": "Delayed launch by 2-4 weeks",
                "mitigation": "Define an explicit MVP boundary and cut criteria",
            },
            {
                "risk": "Third-party dependency",
                "impact": "Feature blocked if vendor API changes",
                "mitigation": "Abstract vendor integration behind an adapter layer",
            },
        ],
        "questions": [
            "What is the expected DAU at launch?",
            "How will success be measured after 30 days?",
            "Is there a rollback plan if metrics regress?",
        ],
        "metrics": [
            {"metric": "Activation rate", "definition": "% of new users completing onboarding within 24h"},
            {"metric": "Task completion time", "definition": "Median seconds to finish the core workflow"},
        ],
        "suggested_experiments": [
            {
                "hypothesis": "Simplifying onboarding increases activation by 15%",
                "metric": "Activation rate",
                "design": "A/B test with 50/50 split over 2 weeks",
            },
        ],
        "decision_trace": {
            "scoring_rubric": rubric_items,
            "assumptions": [
                "The target market size estimate is accurate",
                "Engineering capacity is available as planned",
                "No regulatory blockers in target geographies",
            ],
            "confidence": confidence,
            "impact_profile": impact_profile,
            "readiness_level": readiness_level,
        },
    }


# ── Mode selection ───────────────────────────────────────────────────────────


def _should_use_mock(request: ReviewRequest) -> bool:
    if request.mode == "mock":
        return True
    if request.mode == "auto" and settings.openai_api_key:
        return False
    if settings.openai_api_key:
        return False
    return True


def review_prd(request: ReviewRequest) -> ReviewResponse:
    if _should_use_mock(request):
        logger.info("Using mock reviewer (no API key or mock mode requested)")
        data = _mock_review(request)
    else:
        logger.info("Using OpenAI reviewer (model=%s)", settings.openai_model)
        from app.services.llm_openai import call_openai

        data = call_openai(request.prd_markdown, request.product_context, request.audience)

    return ReviewResponse.model_validate(data)
