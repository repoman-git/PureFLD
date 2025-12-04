"""Cycle-Aware ATR"""
import pandas as pd

class CycleATR:
    def compute(self, price, phase_vel):
        tr = price.rolling(14).max() - price.rolling(14).min()
        atr = tr.rolling(14).mean()
        
        # Cycle slope influence
        slope_factor = (phase_vel.abs() / (phase_vel.abs().rolling(50).mean() + 1e-6))
        slope_factor = slope_factor.clip(0.5, 2).fillna(1)
        
        catr = atr * slope_factor
        return catr.rename("catr").fillna(0)

