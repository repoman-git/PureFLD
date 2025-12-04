"""
Momentum-ETF Strategy

Classic momentum strategy for ETF rotation.
Great for SPY/QQQ/TLT/UUP rotation logic.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class MomentumETF:
    """
    Momentum-based ETF strategy.
    
    Buys when recent momentum is positive, sells when negative.
    Perfect for trend-following in liquid ETFs.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize Momentum-ETF strategy.
        
        Args:
            params: Dictionary with:
                - lookback: Momentum calculation period (default: 60)
                - hold: Minimum holding period (default: 20)
                - threshold: Minimum momentum for signal (default: 0.0)
        """
        self.lookback = params.get("lookback", 60)
        self.hold = params.get("hold", 20)
        self.threshold = params.get("threshold", 0.0)
        
        self.name = "Momentum-ETF"
        self.params = params
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate momentum signals"""
        df = df.copy()
        
        # Calculate momentum (% change over lookback period)
        df["momentum"] = df["close"] / df["close"].shift(self.lookback) - 1
        
        # Generate signals based on momentum
        df["long_signal"] = (df["momentum"] > self.threshold).astype(int)
        df["short_signal"] = (df["momentum"] < -self.threshold).astype(int)
        
        # Add momentum strength for analysis
        df["signal_strength"] = abs(df["momentum"])
        
        return df
    
    def get_param_space(self) -> Dict[str, Any]:
        """Get parameter space for evolution/RL"""
        return {
            'lookback': (20, 120),
            'hold': (5, 40),
            'threshold': (0.0, 0.10)
        }


