"""Regime Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries, RegimeResponse
from ..core.engine_loader import loader
from meridian_v2_1_2.regimes import RegimeType
import pandas as pd

router = APIRouter(prefix="/regime", tags=["Regime"])

@router.post("/classify", response_model=RegimeResponse)
async def classify_regime(request: PriceSeries):
    """Classify market regime"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        features = loader.regime_classifier.extract_features(price)
        labels = loader.regime_classifier.label_regimes(features)
        
        if not loader.regime_classifier.is_trained:
            loader.regime_classifier.train(features, labels, verbose=False)
        
        predictions = loader.regime_classifier.predict(features)
        current = predictions.iloc[-1]
        
        return RegimeResponse(
            regime=int(current['regime']),
            regime_name=current['regime_name'],
            confidence=float(current['regime_confidence']),
            trade_suitability=float(current['trade_suitability'])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

