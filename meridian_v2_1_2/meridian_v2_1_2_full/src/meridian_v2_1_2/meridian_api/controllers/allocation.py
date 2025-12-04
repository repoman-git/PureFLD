"""Allocation Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import IntermarketRequest, AllocationResponse
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/allocation", tags=["Allocation"])

@router.post("/compute", response_model=AllocationResponse)
async def compute_allocation(request: IntermarketRequest):
    """Compute portfolio allocation"""
    try:
        price_dict = {sym: pd.Series(data.prices, index=pd.to_datetime(data.timestamps))
                     for sym, data in request.markets.items()}
        
        features = loader.portfolio_feature_builder.build_features(price_dict)
        weights = loader.portfolio_allocator.allocate(features, 
                                                      loader.cycle_weighting_model,
                                                      loader.portfolio_risk_model)
        
        latest_weights = {col: float(weights[col].iloc[-1]) for col in weights.columns}
        
        return AllocationResponse(
            weights=latest_weights,
            risk_metrics={"total_exposure": sum(abs(w) for w in latest_weights.values())}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

