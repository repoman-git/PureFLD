"""Risk Model - Produces per-asset risk multipliers"""
import pandas as pd
import numpy as np

class PortfolioRiskModel:
    def risk_weight(self, df: pd.DataFrame) -> pd.Series:
        """Calculate risk weight (0-1) for position sizing"""
        out = pd.Series(1.0, index=df.index)
        
        # Volatility adjustment
        vol_norm = df["volatility"] / (df["volatility"].rolling(50).mean() + 1e-10)
        out *= 1 / (1 + vol_norm.fillna(1))
        
        # Turning point proximity
        out *= (1 - 0.5 * df.get("tp_proximity", 0))
        
        # Regime multipliers
        regime_mult = df["regime"].map({0: 0.3, 1: 1.0, 2: 0.5, 3: 0.7, 4: 0.2})
        out *= regime_mult.fillna(1.0) * df.get("regime_confidence", 1.0)
        
        return out.clip(lower=0.01, upper=1.0)

