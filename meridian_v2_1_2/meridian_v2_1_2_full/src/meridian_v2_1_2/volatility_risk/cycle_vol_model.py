"""Cycle Volatility Model"""
import pandas as pd

class CycleVolatilityModel:
    def compute(self, amp, vol, tp_flag):
        amp_norm = amp / (amp.rolling(50).mean() + 1e-6)
        tp_spike = tp_flag * 1.5
        vcycle = (amp_norm + tp_spike).fillna(0)
        return vcycle.rename("vcycle")

