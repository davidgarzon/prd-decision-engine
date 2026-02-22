from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────


class ReviewRequest(BaseModel):
    prd_markdown: str = Field(..., min_length=1, description="PRD content in Markdown")
    product_context: dict | None = Field(default=None, description="Optional product context")
    audience: str | None = Field(default=None, description="Target audience for the review")
    mode: Literal["auto", "mock"] | None = Field(
        default=None,
        description="Execution mode: 'auto' selects LLM when available, 'mock' forces deterministic output",
    )


# ── Response building blocks ─────────────────────────────────────────────────


class Gap(BaseModel):
    area: str
    why: str
    suggested_fix: str


class Risk(BaseModel):
    risk: str
    impact: str
    mitigation: str


class Metric(BaseModel):
    metric: str
    definition: str


class Experiment(BaseModel):
    hypothesis: str
    metric: str
    design: str


class ScoringRubricItem(BaseModel):
    criterion: str
    weight: int = Field(..., ge=0)
    score: int = Field(..., ge=0)
    notes: str

    def model_post_init(self, __context: object) -> None:
        if self.score > self.weight:
            raise ValueError(f"score ({self.score}) must not exceed weight ({self.weight})")


RiskLevel = Literal["low", "medium", "high"]
ReadinessLevel = Literal["Draft", "Pre-Discovery", "Validation Ready", "Build Ready", "Board Ready"]


class ImpactProfile(BaseModel):
    delivery_risk: RiskLevel
    strategic_alignment: RiskLevel
    measurement_maturity: RiskLevel


class DecisionTrace(BaseModel):
    scoring_rubric: list[ScoringRubricItem]
    assumptions: list[str]
    confidence: int = Field(..., ge=0, le=100)
    impact_profile: ImpactProfile
    readiness_level: ReadinessLevel


# ── Response ─────────────────────────────────────────────────────────────────


class ReviewResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    summary: str
    strengths: list[str] = Field(..., max_length=6)
    gaps: list[Gap] = Field(..., max_length=10)
    risks: list[Risk] = Field(..., max_length=8)
    questions: list[str] = Field(..., max_length=12)
    metrics: list[Metric] = Field(..., max_length=8)
    suggested_experiments: list[Experiment] = Field(..., max_length=5)
    decision_trace: DecisionTrace
