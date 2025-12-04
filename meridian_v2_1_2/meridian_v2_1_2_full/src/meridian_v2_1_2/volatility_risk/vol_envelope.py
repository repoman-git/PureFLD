"""Volatility Envelope"""
import pandas as pd

class VolatilityEnvelope:
    def compute(self, vol, window=40, k=2):
        mu = vol.rolling(window).mean()
        sigma = vol.rolling(window).std()
        upper = (mu + k * sigma).fillna(0)
        lower = (mu - k * sigma).fillna(0)
        return {"upper": upper.rename("vol_env_upper"), "lower": lower.rename("vol_env_lower")}

