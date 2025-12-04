"""API Schemas (Pydantic models)"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class PriceSeries(BaseModel):
    timestamps: List[str] = Field(..., description="ISO date strings")
    prices: List[float] = Field(..., description="Price values")

class PhasingRequest(BaseModel):
    price_series: PriceSeries
    periods: Optional[List[int]] = Field(default=[20, 40, 80])

class PhasingResponse(BaseModel):
    phasing_results: Dict
    dominant_period: int
    status: str = "success"

class HarmonicsResponse(BaseModel):
    harmonics: Dict
    dominant_frequency: float
    status: str = "success"

class ForecastResponse(BaseModel):
    forecast_values: List[float]
    forecast_timestamps: List[str]
    confidence: float
    status: str = "success"

class IntermarketRequest(BaseModel):
    markets: Dict[str, PriceSeries]

class IntermarketResponse(BaseModel):
    lead_lag_matrix: Dict
    pressure_vector: Dict
    status: str = "success"

class RegimeResponse(BaseModel):
    regime: int
    regime_name: str
    confidence: float
    trade_suitability: float
    status: str = "success"

class AllocationResponse(BaseModel):
    weights: Dict[str, float]
    risk_metrics: Dict
    status: str = "success"

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float

