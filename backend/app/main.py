"""
Solar Panel Simulator - FastAPI Application
REST API for solar energy production simulation
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.calculator import simulate
from app.models import SolarInput, SolarOutput
from app.validation import validate_input

load_dotenv()

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


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/simulate", response_model=SolarOutput, tags=["simulation"])
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
        return result
    except Exception as e:
        error_detail = (
            "Simulation failed. Please try again."
            if env == "production"
            else f"Simulation error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=error_detail)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
