"""Risk Window Model"""
import pandas as pd

class RiskWindowModel:
    def compute(self, vol, vol_env_upper, vol_env_lower, phase_vel, amp, tp_flag):
        df = pd.DataFrame(index=vol.index)
        df["vol_comp"] = (vol_env_lower - vol).clip(lower=0)
        df["vol_exp"] = (vol - vol_env_upper).clip(lower=0)
        df["accel"] = phase_vel.abs()
        df["amp_norm"] = amp / (amp.rolling(50).mean() + 1e-6)
        df["tp_risk"] = tp_flag
        
        rws = (0.3 * df["vol_comp"] + 0.3 * df["vol_exp"] + 
               0.2 * df["accel"] + 0.1 * df["amp_norm"] + 0.1 * df["tp_risk"])
        return rws.fillna(0).rename("risk_window_score")

