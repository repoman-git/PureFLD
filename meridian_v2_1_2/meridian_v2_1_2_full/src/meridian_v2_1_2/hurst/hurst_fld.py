"""
Forward Line Displacement (FLD) Engine

Computes FLD series, crosses, and envelopes for cycle analysis.

FLD is a core Hurst concept:
- FLD = price shifted forward by half the cycle period
- FLD crosses indicate trend changes
- FLD envelope provides support/resistance zones

This is fundamental to Sentient Trader analysis.
"""

import pandas as pd
import numpy as np


class FLDEngine:
    """
    Forward Line Displacement (FLD) engine.
    
    Computes:
      - FLD series (shifted price)
      - FLD crosses (long/short)
      - FLD envelope
    """

    def __init__(self, period: int):
        self.period = period
        self.shift = int(period / 2)  # Hurst rule: shift = P/2

    def compute_fld(self, price: pd.Series) -> pd.Series:
        """
        Classic FLD: price shifted forward by half its cycle length.
        
        Args:
            price: Price series
        
        Returns:
            FLD series (shifted price)
        
        Example:
            >>> engine = FLDEngine(period=40)
            >>> fld = engine.compute_fld(price)
            >>> # FLD is price shifted 20 bars forward
        """
        fld = price.shift(self.shift)
        fld.name = f"FLD_{self.period}"
        return fld

    def detect_crosses(self, price: pd.Series, fld: pd.Series):
        """
        FLD cross detection (entry signals).
        
        - Price crosses ABOVE FLD → Long signal
        - Price crosses BELOW FLD → Short signal
        
        Args:
            price: Price series
            fld: FLD series
        
        Returns:
            dict with:
              "long_crosses": [timestamps]
              "short_crosses": [timestamps]
        
        Example:
            >>> crosses = engine.detect_crosses(price, fld)
            >>> print(f"Long signals: {len(crosses['long_crosses'])}")
        """
        long_crosses = []
        short_crosses = []

        for i in range(1, len(price)):
            p_prev = price.iloc[i - 1]
            p_curr = price.iloc[i]
            f_prev = fld.iloc[i - 1]
            f_curr = fld.iloc[i]

            if pd.isna(f_prev) or pd.isna(f_curr):
                continue

            # Price crosses ABOVE FLD → long
            if p_prev < f_prev and p_curr > f_curr:
                long_crosses.append(price.index[i])

            # Price crosses BELOW FLD → short
            if p_prev > f_prev and p_curr < f_curr:
                short_crosses.append(price.index[i])

        return {
            "long_crosses": long_crosses,
            "short_crosses": short_crosses,
        }

    def compute_envelope(self, price: pd.Series, bandwidth=0.02):
        """
        Simple FLD envelope for visualization:
        upper = FLD * (1 + bandwidth)
        lower = FLD * (1 - bandwidth)
        
        Args:
            price: Price series
            bandwidth: Envelope width (default: 2%)
        
        Returns:
            Tuple of (upper, lower) series
        
        Example:
            >>> upper, lower = engine.compute_envelope(price, bandwidth=0.02)
            >>> # Creates 2% envelope around FLD
        """
        fld = self.compute_fld(price)
        upper = fld * (1 + bandwidth)
        lower = fld * (1 - bandwidth)
        return upper, lower


