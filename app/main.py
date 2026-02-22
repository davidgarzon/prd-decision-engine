from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.settings import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Automated PRD review engine powered by LLM analysis",
)

app.include_router(router)
