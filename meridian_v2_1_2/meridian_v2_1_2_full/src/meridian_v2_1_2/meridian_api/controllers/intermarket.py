"""Intermarket Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import IntermarketRequest, IntermarketResponse
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/intermarket", tags=["Intermarket"])

@router.post("/analysis", response_model=IntermarketResponse)
async def analyze_intermarket(request: IntermarketRequest):
    """Analyze cross-market relationships"""
    try:
        price_dict = {sym: pd.Series(data.prices, index=pd.to_datetime(data.timestamps)) 
                     for sym, data in request.markets.items()}
        result = loader.intermarket.analyze(price_dict)
        return IntermarketResponse(
            lead_lag_matrix=result.get("lead_lag", {}),
            pressure_vector=result.get("pressure_vector", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

