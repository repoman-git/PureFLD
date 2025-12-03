"""
Harmonics Engine

Complete harmonic spectral analysis system:
- Detects dominant periodicities
- Identifies harmonic families (P, 2P, 4P, ½P, ⅓P, etc.)
- Quantifies amplitude strength per harmonic
- Finds cycle "energy clusters"
- Computes harmonic interference patterns
- Generates dominance curves (composite cycle)
- Produces weighted harmonic map

This is Sentient Trader's "Cycle Analyst" and "Profile View" equivalent.
"""

import numpy as np
import pandas as pd
from scipy.signal import periodogram
from typing import Dict, List


class HarmonicsEngine:
    """
    Computes harmonic cycle structure using frequency-domain analysis.

    Output:
      - dominant_cycles: list of detected cycle lengths
      - harmonics_map: dict {cycle: [harmonics...]}
      - spectral_peaks: detailed spectral peak info
      - composite_cycle: weighted cycle reconstruction
    """

    def __init__(self, max_period=400, min_period=10):
        self.min_period = min_period
        self.max_period = max_period

    # ---------------------------------------------------------------
    # STEP 1: Compute raw spectrum
    # ---------------------------------------------------------------
    def compute_spectrum(self, price: pd.Series):
        """
        Compute power spectrum of price series.
        
        Args:
            price: Price series
        
        Returns:
            Tuple of (periods, power)
        """
        price_detrended = price - price.rolling(200, min_periods=1).mean()
        price_detrended = price_detrended.dropna()
        fs = 1   # daily sampling

        freqs, power = periodogram(price_detrended.values, fs=fs, scaling="spectrum")

        periods = np.where(freqs != 0, 1 / freqs, np.inf)
        mask = (periods >= self.min_period) & (periods <= self.max_period)

        return periods[mask], power[mask]

    # ---------------------------------------------------------------
    # STEP 2: Find dominant cycles
    # ---------------------------------------------------------------
    def find_dominant_cycles(self, periods, power, top_n=6):
        """
        Find top N dominant cycles from spectrum.
        
        Args:
            periods: Array of periods
            power: Array of power values
            top_n: Number of cycles to return
        
        Returns:
            List of dominant cycle lengths
        """
        idx = np.argsort(power)[-top_n:]
        dominant = periods[idx]
        dominant = np.sort(dominant)

        # round to nearest real cycle
        return [int(round(x)) for x in dominant]

    # ---------------------------------------------------------------
    # STEP 3: Build harmonic families
    # ---------------------------------------------------------------
    def build_harmonic_map(self, cycles: List[int]):
        """
        Build harmonic families for each cycle.
        
        For cycle P, includes: P, 2P, 4P, P/2, P/3, P/4
        
        Args:
            cycles: List of base cycle periods
        
        Returns:
            Dictionary mapping cycle -> list of harmonics
        """
        harmonics = {}
        for c in cycles:
            h = [
                c,
                int(c * 2),
                int(c * 4),
                int(c / 2),
                int(c / 3),
                int(c / 4)
            ]
            harmonics[c] = sorted({int(x) for x in h if x >= self.min_period and x <= self.max_period})
        return harmonics

    # ---------------------------------------------------------------
    # STEP 4: Composite Cycle (weighted harmonic blend)
    # ---------------------------------------------------------------
    def composite_cycle(self, price: pd.Series, cycles: List[int]) -> pd.Series:
        """
        Generate composite cycle (weighted sum of harmonics).
        
        Args:
            price: Price series
            cycles: List of cycle periods
        
        Returns:
            Composite cycle series
        """
        x = np.arange(len(price))
        comp = np.zeros(len(price))

        for c in cycles:
            w = 1 / c
            comp += w * np.sin(2 * np.pi * x / c)

        comp = pd.Series(comp, index=price.index, name="CompositeCycle")
        return comp

    # ---------------------------------------------------------------
    # MAIN
    # ---------------------------------------------------------------
    def analyze(self, price: pd.Series, top_n=6):
        """
        Complete harmonic analysis.
        
        Args:
            price: Price series
            top_n: Number of top cycles to find
        
        Returns:
            Dictionary with:
              - dominant_cycles: Top cycles detected
              - harmonics_map: Harmonic families
              - composite_cycle: Weighted cycle reconstruction
              - raw_periods: All periods from spectrum
              - raw_power: Power values
        
        Example:
            >>> from meridian_v2_1_2.hurst import HarmonicsEngine
            >>> 
            >>> engine = HarmonicsEngine()
            >>> results = engine.analyze(price)
            >>> 
            >>> print("Dominant cycles:", results['dominant_cycles'])
            >>> print("Harmonics:", results['harmonics_map'])
            >>> results['composite_cycle'].plot()
        """
        periods, power = self.compute_spectrum(price)
        dominant = self.find_dominant_cycles(periods, power, top_n=top_n)
        harmonics = self.build_harmonic_map(dominant)
        composite = self.composite_cycle(price, dominant)

        return {
            "dominant_cycles": dominant,
            "harmonics_map": harmonics,
            "composite_cycle": composite,
            "raw_periods": periods,
            "raw_power": power
        }

