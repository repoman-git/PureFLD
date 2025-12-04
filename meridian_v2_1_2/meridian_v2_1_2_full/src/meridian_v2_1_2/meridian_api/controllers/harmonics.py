"""Harmonics Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries, HarmonicsResponse
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/harmonics", tags=["Harmonics"])

@router.post("/compute", response_model=HarmonicsResponse)
async def compute_harmonics(request: PriceSeries):
    """Compute spectral harmonics"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        result = loader.harmonics.analyze(price)
        return HarmonicsResponse(harmonics=result, dominant_frequency=result.get("dominant_frequency", 0))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

