"""
Meridian Cycle Intelligence API Server

FastAPI application exposing all Meridian capabilities.

Launch: uvicorn meridian_v2_1_2.meridian_api.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from .schemas import HealthResponse
from .controllers import phasing, harmonics, forecast, intermarket, regime, volatility, allocation, strategy

# Initialize FastAPI
app = FastAPI(
    title="Meridian Cycle Intelligence API",
    description="Institutional-grade cycle analytics platform - Stage 6",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track startup time
START_TIME = time.time()

# Include routers
app.include_router(phasing.router, prefix="/api/v2")
app.include_router(harmonics.router, prefix="/api/v2")
app.include_router(forecast.router, prefix="/api/v2")
app.include_router(intermarket.router, prefix="/api/v2")
app.include_router(regime.router, prefix="/api/v2")
app.include_router(volatility.router, prefix="/api/v2")
app.include_router(allocation.router, prefix="/api/v2")
app.include_router(strategy.router, prefix="/api/v2")

@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "Meridian Cycle Intelligence API",
        "version": "2.0.0",
        "stage": "6 of 10",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        uptime_seconds=time.time() - START_TIME
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

