"""Phasing Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries, PhasingResponse
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/phasing", tags=["Phasing"])

@router.post("/compute", response_model=PhasingResponse)
async def compute_phasing(request: PriceSeries, period: int = 40):
    """Compute Hurst cycle phasing"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        result = loader.phaser.compute_phase(price, period)
        return PhasingResponse(
            phasing_results={"phase": result.get("phase", []).tolist() if hasattr(result.get("phase"), "tolist") else []},
            dominant_period=period
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

