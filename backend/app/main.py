"""
Solar Panel Simulator - FastAPI Application
REST API for solar energy production simulation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import SolarInput, SolarOutput, ValidationError as ValidationErrorModel
from app.calculator import simulate
from app.validation import validate_input

app = FastAPI(
    title="Solar Panel Simulator API",
    description="Calculate solar panel energy production and savings",
    version="1.0.0"
)

# Enable CORS for frontend (localhost:3000 for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            detail=[{"field": e.field, "message": e.message} for e in validation_errors]
        )

    try:
        # Run simulation
        result = simulate(input_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
