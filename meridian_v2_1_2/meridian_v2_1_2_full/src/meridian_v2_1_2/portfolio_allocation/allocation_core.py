"""Portfolio Allocator - Combines signals into final weights"""
import pandas as pd
import numpy as np
from typing import Dict

class PortfolioAllocator:
    def allocate(self, feature_dict: Dict[str, pd.DataFrame], cycle_model, risk_model) -> pd.DataFrame:
        """Generate portfolio weights"""
        weights = {}
        
        for symbol, df in feature_dict.items():
            cycle_strength = cycle_model.cycle_strength(df)
            risk_weight = risk_model.risk_weight(df)
            pressure = df.get("intermarket_pressure", 0)
            
            # Combined weight
            w = cycle_strength * risk_weight * (1 + pressure)
            weights[symbol] = w
        
        # Normalize to sum to 1
        weights_df = pd.DataFrame(weights)
        weights_df = weights_df.div(weights_df.abs().sum(axis=1) + 1e-10, axis=0).fillna(0)
        
        return weights_df

