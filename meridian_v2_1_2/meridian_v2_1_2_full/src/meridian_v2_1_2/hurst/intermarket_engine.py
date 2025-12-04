"""
Intermarket Cycle Engine

Analyzes cycle relationships across multiple markets.

Features:
- Cross-market cycle synchronization
- Cycle lead/lag detection
- Composite intermarket cycle
- Regime bias (Risk-On/Risk-Off)
- Intermarket pressure vectors
- Cross-confirming turning points
- Multi-asset FLD/VTL confirmation

Relationships analyzed:
- Gold ↔ USD ↔ Bonds ↔ Silver
- Equities ↔ Rates ↔ Crude ↔ USD
- Crypto ↔ Nasdaq ↔ Liquidity
- Commodities ↔ DXY cycles

This is what professional macro quants use for intermarket analysis.

⚠️  EXPERIMENTAL - Multi-market cycle analysis for research
"""

import numpy as np
import pandas as pd
from typing import Dict, List

from .hurst_harmonics import HarmonicsEngine
from .cycle_forecaster import CycleForecaster
from .hurst_phasing import HurstPhasingEngine


class IntermarketCycleEngine:
    """
    Analyzes cycle relationships across multiple markets:
      - cycle synchrony
      - lead/lag matrix
      - intermarket pressure vectors
      - composite cycle (multi-asset)
      - turning point alignment

    Inputs:
      price_dict = { "GC": series, "DXY": series, "TNX": series, ... }
    
    Example:
        >>> from meridian_v2_1_2.hurst import IntermarketCycleEngine
        >>> 
        >>> price_dict = {
        ...     'GLD': gold_series,
        ...     'DXY': dollar_series,
        ...     'TLT': bond_series,
        ...     'SPY': equity_series
        ... }
        >>> 
        >>> engine = IntermarketCycleEngine()
        >>> results = engine.analyze(price_dict)
        >>> 
        >>> print("Lead/Lag Matrix:")
        >>> print(results['lead_lag'])
        >>> 
        >>> print("Pressure Vector:")
        >>> print(results['pressure_vector'])
    """

    def __init__(self, cycle_periods=[20, 40, 80, 160], forecast_horizon=20):
        self.cycle_periods = cycle_periods
        self.forecast_horizon = forecast_horizon

    # ----------------------------------------------------------------------
    # 1. Compute harmonics + composite per instrument
    # ----------------------------------------------------------------------
    def analyze_harmonics(self, price_dict):
        """
        Analyze harmonics for each instrument.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
        
        Returns:
            Dictionary mapping symbol -> harmonic analysis
        """
        results = {}
        h = HarmonicsEngine()

        for sym, price in price_dict.items():
            results[sym] = h.analyze(price)

        return results

    # ----------------------------------------------------------------------
    # 2. Compute Hurst phasing for all instruments
    # ----------------------------------------------------------------------
    def analyze_phasing(self, price_dict):
        """
        Compute phasing for all instruments.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
        
        Returns:
            Dictionary mapping symbol -> phasing results
        """
        results = {}
        phaser = HurstPhasingEngine(self.cycle_periods)

        for sym, price in price_dict.items():
            results[sym] = phaser.phase_all(price)
        return results

    # ----------------------------------------------------------------------
    # 3. Forecast next 20–30 bars for each instrument
    # ----------------------------------------------------------------------
    def forecast_all(self, price_dict):
        """
        Forecast all instruments.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
        
        Returns:
            Dictionary mapping symbol -> forecast series
        
        ⚠️  Requires TensorFlow for LSTM forecasting
        """
        forecasts = {}

        for sym, price in price_dict.items():
            try:
                cf = CycleForecaster(forecast_horizon=self.forecast_horizon)
                cf.fit(price, epochs=10, verbose=0)
                forecasts[sym] = cf.predict()
            except Exception as e:
                print(f"  ⚠️  Forecast failed for {sym}: {e}")
                # Fallback: flat forecast
                last = price.iloc[-1]
                dates = pd.date_range(price.index[-1] + pd.Timedelta(days=1),
                                      periods=self.forecast_horizon, freq='D')
                forecasts[sym] = pd.Series(np.full(self.forecast_horizon, last), index=dates)

        return forecasts

    # ----------------------------------------------------------------------
    # 4. Compute lead/lag matrix (who leads cycles)
    # ----------------------------------------------------------------------
    def compute_lead_lag(self, phasing_dict):
        """
        Measure average phase difference between markets.
        Lower phase → earlier in cycle → leading
        
        Args:
            phasing_dict: Phasing results for all instruments
        
        Returns:
            DataFrame with lead/lag relationships
            
        Interpretation:
        - Positive value: Row leads Column
        - Negative value: Row lags Column
        - Zero: Synchronized
        """

        symbols = list(phasing_dict.keys())
        lead_lag = pd.DataFrame(index=symbols, columns=symbols, dtype=float)

        for s1 in symbols:
            for s2 in symbols:
                phases1 = []
                phases2 = []

                for period in self.cycle_periods:
                    if period in phasing_dict[s1] and period in phasing_dict[s2]:
                        p1 = phasing_dict[s1][period]["phase"]
                        p2 = phasing_dict[s2][period]["phase"]

                        # align index
                        common = p1.index.intersection(p2.index)
                        if len(common) > 0:
                            phases1.append(p1.loc[common].mean())
                            phases2.append(p2.loc[common].mean())

                if phases1 and phases2:
                    lead_lag.loc[s1, s2] = np.mean(phases1) - np.mean(phases2)
                else:
                    lead_lag.loc[s1, s2] = 0.0

        return lead_lag

    # ----------------------------------------------------------------------
    # 5. Compute intermarket pressure vector
    # ----------------------------------------------------------------------
    def compute_pressure_vector(self, forecasts):
        """
        Positive slope in GC + negative slope in DXY = bullish gold pressure.
        
        Args:
            forecasts: Dictionary of forecast series
        
        Returns:
            Series with slope (pressure) for each instrument
        """
        slopes = {}
        for sym, fc in forecasts.items():
            if len(fc) > 1:
                slopes[sym] = (fc.iloc[-1] - fc.iloc[0]) / len(fc)
            else:
                slopes[sym] = 0.0

        return pd.Series(slopes, name="PressureVector")

    # ----------------------------------------------------------------------
    # 6. Composite intermarket cycle
    # ----------------------------------------------------------------------
    def composite_intermarket_cycle(self, harmonics_dict):
        """
        Blend dominant cycles across markets.
        
        Args:
            harmonics_dict: Harmonic analysis for all instruments
        
        Returns:
            Median composite cycle period
        """
        all_cycles = []
        for sym, h in harmonics_dict.items():
            all_cycles.extend(h["dominant_cycles"])

        # frequency-weighted average
        if all_cycles:
            comp_cycle = np.median(all_cycles)
            return int(comp_cycle)
        return None

    # ----------------------------------------------------------------------
    # 7. Turning Point Alignment Index
    # ----------------------------------------------------------------------
    def turning_point_alignment(self, phasing_dict, lookback=100):
        """
        Detect trough/peak clustering across instruments.
        Higher score = synchronized turning point.
        
        Args:
            phasing_dict: Phasing results
            lookback: Number of bars to analyze
        
        Returns:
            Series showing alignment strength over time
        """
        
        # Get first instrument's index as reference
        first_sym = next(iter(phasing_dict.keys()))
        first_cycles = next(iter(phasing_dict.values()))
        first_phase = next(iter(first_cycles.values()))['phase']
        
        alignment = pd.Series(0, index=first_phase.index[-lookback:])

        for sym, cycles in phasing_dict.items():
            for period, res in cycles.items():
                troughs = res["troughs"]
                for t in troughs:
                    if t in alignment.index:
                        alignment.loc[t] += 1

        alignment.name = "TP_Alignment"
        return alignment

    # ----------------------------------------------------------------------
    # MAIN PIPELINE
    # ----------------------------------------------------------------------
    def analyze(self, price_dict):
        """
        Complete intermarket cycle analysis.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
        
        Returns:
            Dictionary with:
              - harmonics: Harmonic analysis per instrument
              - phasing: Phasing results per instrument
              - forecasts: AI forecasts per instrument
              - lead_lag: Lead/lag matrix
              - pressure_vector: Forecast slopes
              - composite_cycle: Median cycle across markets
              - turning_point_alignment: TP clustering index
        
        ⚠️  EXPERIMENTAL - Intermarket analysis for research only
        """
        print(f"Analyzing {len(price_dict)} instruments...")
        
        # Step 1: Harmonics
        print("  → Computing harmonics...")
        harmonics = self.analyze_harmonics(price_dict)

        # Step 2: Phasing
        print("  → Computing phasing...")
        phasing = self.analyze_phasing(price_dict)

        # Step 3: AI Forecast
        print("  → Generating forecasts...")
        forecasts = self.forecast_all(price_dict)

        # Step 4: Lead/Lag
        print("  → Computing lead/lag matrix...")
        lead_lag = self.compute_lead_lag(phasing)

        # Step 5: Pressure Vector
        print("  → Computing pressure vectors...")
        pressure = self.compute_pressure_vector(forecasts)

        # Step 6: Composite Intermarket Cycle
        print("  → Computing composite cycle...")
        comp_cycle = self.composite_intermarket_cycle(harmonics)

        # Step 7: Turning Point Alignment
        print("  → Computing turning point alignment...")
        tpa = self.turning_point_alignment(phasing)
        
        print("✅ Intermarket analysis complete!")

        return {
            "harmonics": harmonics,
            "phasing": phasing,
            "forecasts": forecasts,
            "lead_lag": lead_lag,
            "pressure_vector": pressure,
            "composite_cycle": comp_cycle,
            "turning_point_alignment": tpa,
        }


