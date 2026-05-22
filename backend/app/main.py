"""
Solar Panel Simulator - FastAPI Application
REST API for solar energy production simulation
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.calculator import simulate
from app.models import SolarInput, SolarOutput
from app.validation import validate_input

load_dotenv()

app = FastAPI(
    title="Solar Panel Simulator API",
    description="Calculate solar panel energy production and savings",
    version="1.0.0",
)

env = os.getenv("ENV", "development")
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Enable CORS for frontend (configurable per environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=env != "production",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/simulate", response_model=SolarOutput, tags=["simulation"])
async def simulate_solar_system(input_data: SolarInput):
    """
    Simulate solar panel energy production.

    Takes solar system parameters and returns annual/daily/monthly energy metrics.
    """
    # Validate input
    validation_errors = validate_input(input_data)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail=[{"field": e.field, "message": e.message} for e in validation_errors],
        )

    try:
        # Run simulation
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
