"""Rule Library - Generates signals from genome"""
import pandas as pd
import numpy as np

class RuleLibrary:
    """Contains rule functions using cycle/volatility/risk intelligence"""
    
    def generate_signals(self, price, phasing=None, fld=None, vtl=None, vol_df=None, forecast=None, genome=None):
        """Generate trading signals from genome"""
        df = pd.DataFrame(index=price.index)
        df["signal"] = 1  # Start with all buy signals
        
        # FLD rule (if available)
        if fld is not None:
            offset = int(genome.genes["fld_offset"])
            df["fld_cross"] = (price > fld.shift(offset)).astype(int).fillna(1)
            df["signal"] *= df["fld_cross"]
        
        # Cycle amplitude filter
        if vol_df is not None and "amp" in vol_df.columns:
            df["cycle_filter"] = (vol_df["amp"] > genome.genes["cycle_amp_min"]).astype(int).fillna(1)
            df["signal"] *= df["cycle_filter"]
        
        # Volatility filter
        if vol_df is not None and "vol" in vol_df.columns:
            df["vol_filter"] = (vol_df["vol"] < genome.genes["vol_thresh"]).astype(int).fillna(1)
            df["signal"] *= df["vol_filter"]
        
        # Risk Window constraint
        if vol_df is not None and "risk_window_score" in vol_df.columns:
            df["rws_filter"] = (vol_df["risk_window_score"] < genome.genes["rws_limit"]).astype(int).fillna(1)
            df["signal"] *= df["rws_filter"]
        
        # Forecast slope direction
        if forecast is not None and len(forecast) > 1:
            slope = (forecast.iloc[-1] - forecast.iloc[0]) / len(forecast)
            df["forecast_bias"] = int(slope > genome.genes["forecast_slope"])
            df["signal"] *= df["forecast_bias"]
        
        return df["signal"].fillna(0)

