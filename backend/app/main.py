"""
Solar Panel Simulator - FastAPI Application
REST API for solar energy production simulation
"""

import json
import logging
import os
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.calculator import simulate
from app.models import SolarInput
from app.validation import validate_input

load_dotenv()

logger = logging.getLogger(__name__)

env = os.getenv("ENV", "development")
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Solar Panel Simulator API",
    description="Calculate solar panel energy production and savings",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=600,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error("Unhandled exception on %s: %s\n%s", request.url.path, str(exc), tb)
    if env == "production":
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})
    return JSONResponse(
        status_code=500,
        content={"detail": f"{str(exc)}\n\nTraceback:\n{tb}"},
    )


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/simulate", tags=["simulation"])
@limiter.limit(f"{rate_limit_per_minute}/minute")
async def simulate_solar_system(request: Request, input_data: SolarInput):
    """
    Simulate solar panel energy production.

    Rate limited per IP (configured via RATE_LIMIT_PER_MINUTE, default 10/minute).
    """
    validation_errors = validate_input(input_data)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail=[{"field": e.field, "message": e.message} for e in validation_errors],
        )

    try:
        result = simulate(input_data)
        # Exclude None values from response to avoid empty battery fields in legacy requests
        data = json.loads(result.model_dump_json(exclude_none=True))
        return JSONResponse(content=data)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Simulation error: %s\n%s", str(e), tb)
        if env == "production":
            raise HTTPException(status_code=500, detail="Simulation failed. Please try again.")
        raise HTTPException(
            status_code=500,
            detail=f"Simulation error: {str(e)}\n\nTraceback:\n{tb}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
