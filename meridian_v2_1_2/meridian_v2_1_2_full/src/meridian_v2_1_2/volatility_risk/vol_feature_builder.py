"""Volatility Feature Builder"""
import pandas as pd

class VolFeatureBuilder:
    def build(self, price, phasing=None, harmonics=None, regime=None):
        df = pd.DataFrame(index=price.index)
        df["price"] = price
        df["returns"] = price.pct_change()
        df["vol"] = df["returns"].abs().rolling(20).mean()
        df["vol_delta"] = df["vol"].diff()
        
        # Cycle amplitude
        if harmonics and "dominant_amp" in harmonics:
            df["amp"] = harmonics["dominant_amp"]
        else:
            df["amp"] = df["vol"] * 10
        
        # Phase velocity
        if phasing:
            mid_cycle = sorted(phasing.keys())[len(phasing.keys())//2]
            phase_data = phasing[mid_cycle].get("phase", pd.Series(0, index=df.index))
            df["phase_vel"] = phase_data.diff() if isinstance(phase_data, pd.Series) else 0
            
            # Turning points
            df["tp_flag"] = 0
            for t in phasing[mid_cycle].get("troughs", []):
                if t in df.index:
                    df.loc[t, "tp_flag"] = 1
        else:
            df["phase_vel"] = 0
            df["tp_flag"] = 0
        
        # Regime
        if regime is not None:
            common_idx = df.index.intersection(regime.index)
            df.loc[common_idx, "regime"] = regime.loc[common_idx, "regime"]
            df.loc[common_idx, "regime_conf"] = regime.loc[common_idx, "regime_confidence"]
            df["regime"] = df["regime"].fillna(1)
            df["regime_conf"] = df["regime_conf"].fillna(0.5)
        else:
            df["regime"] = 1
            df["regime_conf"] = 0.5
        
        return df.fillna(0)

