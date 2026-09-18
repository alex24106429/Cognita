"""
Cognita - FastAPI service.

Endpoints
---------
GET  /api/health     -> readiness probe with model metadata
POST /api/transform  -> cognitive restructuring of raw academic text
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import TransformRequest, TransformationResponse
from transformer import (
    MalformedModelOutputError,
    ProviderUnavailableError,
    is_api_key_configured,
    get_model_name,
    transform_document,
)

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("cognita-backend")

app = FastAPI(
    title="Cognita Accessibility API",
    version="1.0.0",
    description=(
        "Cognitive accessibility engine that restructures dense academic text for "
        "neurodivergent learners (SDG 10: Reduced Inequalities)."
    ),
)

# --------------------------------------------------------------------------- #
# CORS
# --------------------------------------------------------------------------- #
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation failures into an actionable, friendly payload."""
    details = exc.errors()
    message = "The submitted text failed validation."
    for error in details:
        loc = ".".join(str(part) for part in error.get("loc", ()))
        if loc.endswith("raw_text"):
            if error.get("type") == "string_too_short":
                message = (
                    "The submitted text is too short. Paste at least 100 characters "
                    "of academic material so the engine has enough context."
                )
            elif error.get("type") == "string_too_long":
                message = (
                    "The submitted text exceeds the 50,000 character limit. "
                    "Split the document and transform it in parts."
                )
            else:
                message = "The 'raw_text' field is required and must be a string."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": message, "errors": details},
    )


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.get("/api/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "model": get_model_name(),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "api_key_configured": is_api_key_configured(),
        "cors_origins": origins,
    }


@app.post(
    "/api/transform",
    response_model=TransformationResponse,
    responses={
        422: {"description": "Invalid or insufficient input text"},
        502: {"description": "Provider returned unusable output"},
        503: {"description": "Provider unavailable / rate limited"},
    },
)
async def transform_academic_text(payload: TransformRequest) -> TransformationResponse:
    if not is_api_key_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "OPENAI_API_KEY is not configured on the backend server. "
                "Copy backend/.env.example to backend/.env and add your key."
            ),
        )

    logger.info(
        "Processing transformation request | chars=%s | model=%s",
        len(payload.raw_text),
        get_model_name(),
    )

    try:
        return await transform_document(payload.raw_text)
    except MalformedModelOutputError as exc:
        logger.error("Unusable model output: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The AI provider generated a response that could not be validated "
                "against the Cognita schema. Please retry."
            ),
        ) from exc
    except ProviderUnavailableError as exc:
        logger.error("Provider unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The AI provider is temporarily unavailable or rate limited. "
                "Please wait a moment and try again."
            ),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - final safety net
        logger.exception("Unhandled transformation failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Processing Error: {exc}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
