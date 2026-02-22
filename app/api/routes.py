from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.models.schemas import ReviewRequest, ReviewResponse
from app.services.reviewer import review_prd

router = APIRouter()


@router.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    return review_prd(request)


@router.get("/schema")
def schema() -> dict:
    return ReviewResponse.model_json_schema()
