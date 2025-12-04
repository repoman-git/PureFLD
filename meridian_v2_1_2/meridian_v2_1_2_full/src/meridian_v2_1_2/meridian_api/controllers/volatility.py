"""Volatility Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/volatility", tags=["Volatility"])

@router.post("/model")
async def compute_volatility(request: PriceSeries):
    """Compute volatility metrics"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        df = loader.vol_feature_builder.build(price)
        
        catr = loader.cycle_atr.compute(price, df["phase_vel"])
        vcycle = loader.vol_model.compute(df["amp"], df["vol"], df["tp_flag"])
        
        return {
            "catr": catr.iloc[-1] if len(catr) > 0 else 0,
            "vcycle": vcycle.iloc[-1] if len(vcycle) > 0 else 0,
            "volatility": df["vol"].iloc[-1] if len(df) > 0 else 0,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

