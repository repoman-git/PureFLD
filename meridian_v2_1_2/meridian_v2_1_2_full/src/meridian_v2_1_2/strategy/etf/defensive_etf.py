"""
Defensive-ETF Strategy

Volatility-based defensive positioning.
Best used on TLT, IEF, UUP, XLU as volatility hedges.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class DefensiveETF:
    """
    Defensive ETF strategy based on volatility regimes.
    
    Buys defensive assets (bonds, dollar, utilities) when volatility is low,
    exits or shorts when volatility spikes.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize Defensive-ETF strategy.
        
        Args:
            params: Dictionary with:
                - vol_window: Volatility calculation window (default: 30)
                - threshold: Volatility threshold (default: 0.02)
                - inverse_logic: Inverse signals for anti-defensive (default: False)
        """
        self.vol_window = params.get("vol_window", 30)
        self.threshold = params.get("threshold", 0.02)
        self.inverse_logic = params.get("inverse_logic", False)
        
        self.name = "Defensive-ETF"
        self.params = params
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate volatility-based defensive signals"""
        df = df.copy()
        
        # Calculate rolling volatility (annualized)
        returns = df["close"].pct_change()
        df["volatility"] = returns.rolling(self.vol_window).std() * np.sqrt(252)
        
        # Generate signals
        if not self.inverse_logic:
            # Standard defensive: buy when vol is low
            df["long_signal"] = (df["volatility"] < self.threshold).astype(int)
            df["short_signal"] = (df["volatility"] > self.threshold * 2).astype(int)
        else:
            # Inverse: buy when vol is high (for VXX-like instruments)
            df["long_signal"] = (df["volatility"] > self.threshold).astype(int)
            df["short_signal"] = (df["volatility"] < self.threshold / 2).astype(int)
        
        # Signal strength (how far from threshold)
        df["signal_strength"] = abs(df["volatility"] - self.threshold) / self.threshold
        
        return df
    
    def get_param_space(self) -> Dict[str, Any]:
        """Get parameter space for evolution/RL"""
        return {
            'vol_window': (10, 60),
            'threshold': (0.01, 0.05),
            'inverse_logic': [True, False]
        }

