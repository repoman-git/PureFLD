"""Forecast Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries, ForecastResponse
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.post("/ensemble", response_model=ForecastResponse)
async def forecast_ensemble(request: PriceSeries, horizon: int = 20):
    """Generate ensemble forecast"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        forecast = loader.forecaster.forecast(price, horizon=horizon)
        return ForecastResponse(
            forecast_values=forecast.tolist() if hasattr(forecast, "tolist") else [],
            forecast_timestamps=[str(t) for t in forecast.index] if hasattr(forecast, "index") else [],
            confidence=0.75
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

