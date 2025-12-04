"""
Cycle-ETF Strategy

Hurst-inspired cycle detection for commodity and precious metal ETFs.
Ideal for GDX, XME, GLD.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class CycleETF:
    """
    Cycle-based ETF strategy.
    
    Detects cyclical patterns and trades deviations from mean.
    Works well on commodity ETFs with pronounced cycles.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize Cycle-ETF strategy.
        
        Args:
            params: Dictionary with:
                - length: Cycle length (default: 40)
                - threshold: Signal threshold (default: 0.5)
                - smoothing: MA smoothing period (optional)
        """
        self.length = params.get("length", 40)
        self.threshold = params.get("threshold", 0.5)
        self.smoothing = params.get("smoothing", 5)
        
        self.name = "Cycle-ETF"
        self.params = params
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate cycle-based signals"""
        df = df.copy()
        
        # Calculate cycle deviation (price - rolling mean)
        rolling_mean = df["close"].rolling(self.length).mean()
        df["cycle"] = df["close"] - rolling_mean
        
        # Optionally smooth
        if self.smoothing > 1:
            df["cycle"] = df["cycle"].rolling(self.smoothing).mean()
        
        # Generate signals based on threshold
        df["long_signal"] = (df["cycle"] > self.threshold).astype(int)
        df["short_signal"] = (df["cycle"] < -self.threshold).astype(int)
        
        # Normalized cycle strength
        df["signal_strength"] = abs(df["cycle"]) / df["close"].rolling(self.length).std()
        
        return df
    
    def get_param_space(self) -> Dict[str, Any]:
        """Get parameter space for evolution/RL"""
        return {
            'length': (20, 80),
            'threshold': (0.1, 2.0),
            'smoothing': (1, 10)
        }


