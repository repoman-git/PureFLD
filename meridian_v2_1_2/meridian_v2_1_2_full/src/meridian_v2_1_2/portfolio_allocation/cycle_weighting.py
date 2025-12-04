"""Cycle Weighting Model - Converts cycle analytics into weights"""
import pandas as pd
import numpy as np

class CycleWeightingModel:
    def cycle_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate cycle strength score"""
        strength = pd.Series(0.0, index=df.index)
        
        # Amplitude strength
        amp = df.get("amp_total", df.get("volatility", 1)) * 10
        amp_norm = amp / (amp.rolling(50).mean() + 1e-10)
        strength += amp_norm.clip(0, 2).fillna(1)
        
        # Forecast slope
        slope = df.get("forecast_slope", 0)
        vol = df.get("volatility", 1) + 1e-6
        strength += (slope / vol).fillna(0)
        
        # Phase velocity (momentum)
        phase_vel = df.get("phase_velocity", 0)
        strength += phase_vel.fillna(0) * 0.5
        
        return strength.clip(-2, 2)

