"""
Multi-Cycle Scanner

Scans multiple instruments for cycle synchronization.

Features:
- Scans any symbol list (GC, SI, CL, ES, NQ, EURUSD, BTC, SPY...)
- Computes cycle clusters per instrument
- Scores cycles by strength, stability, and harmonic coherence
- Flags instruments with synchronized cycles
- Detects cross-instrument cycle alignment (VERY powerful)
- Exports daily CSV ranking
- Produces dashboard heatmap of cycle energy

This is Sentient Trader's "Market Synchronization Monitor" equivalent.
"""

import numpy as np
import pandas as pd
from typing import Dict, List

from .hurst_harmonics import HarmonicsEngine


class CycleScanner:
    """
    Scans multiple instruments for cycle synchrony and strength.
    
    Example:
        >>> from meridian_v2_1_2.hurst import CycleScanner
        >>> 
        >>> # Prepare data
        >>> data = {
        ...     'GLD': gold_price_series,
        ...     'SPY': spy_price_series,
        ...     'TLT': tlt_price_series
        ... }
        >>> 
        >>> # Scan for cycles
        >>> scanner = CycleScanner(top_n=6)
        >>> results = scanner.scan(data)
        >>> 
        >>> # Get synchrony map
        >>> sync = scanner.synchrony_map(results)
        >>> print("Instruments sharing 40-day cycle:", sync.get(40, []))
        >>> 
        >>> # Export CSV
        >>> df = scanner.export_csv(results)
    """

    def __init__(self, top_n=6):
        self.top_n = top_n
        self.harm_engine = HarmonicsEngine()

    # ---------------------------------------------------------------
    # Score cycles for one instrument
    # ---------------------------------------------------------------
    def score_cycles(self, symbol: str, price: pd.Series):
        """
        Score cycles for a single instrument.
        
        Args:
            symbol: Instrument symbol
            price: Price series
        
        Returns:
            Dictionary with cycle analysis
        """
        h = self.harm_engine.analyze(price, top_n=self.top_n)
        dominant = h["dominant_cycles"]

        # Score = harmonic density + cycle stability heuristic
        scores = []
        for c in dominant:
            harmonic_count = len(h["harmonics_map"][c])
            stability = 1 / abs(c - np.median(dominant)) if len(dominant) > 1 else 1.0

            score = harmonic_count * stability
            scores.append((c, score))

        ranked = sorted(scores, key=lambda x: x[1], reverse=True)

        return {
            "symbol": symbol,
            "dominant_cycles": dominant,
            "ranked_cycles": ranked,
            "harmonics_map": h["harmonics_map"],
            "composite": h["composite_cycle"],
        }

    # ---------------------------------------------------------------
    # Multi-symbol scan
    # ---------------------------------------------------------------
    def scan(self, price_dict: Dict[str, pd.Series]):
        """
        Scan multiple instruments for cycles.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
        
        Returns:
            Dictionary mapping symbol -> cycle analysis
        """
        results = {}
        for sym, series in price_dict.items():
            results[sym] = self.score_cycles(sym, series)
        return results

    # ---------------------------------------------------------------
    # Create synchrony heatmap data (cycle clusters)
    # ---------------------------------------------------------------
    def synchrony_map(self, scan_results):
        """
        Create synchrony map showing which instruments share cycles.
        
        Args:
            scan_results: Results from scan()
        
        Returns:
            Dictionary mapping cycle -> [(symbol, score), ...]
        
        Example:
            >>> sync = scanner.synchrony_map(results)
            >>> # Show instruments with 40-day cycle
            >>> print("40-day cycle found in:")
            >>> for symbol, score in sync.get(40, []):
            ...     print(f"  {symbol}: {score:.2f}")
        """
        cluster = {}

        for sym, res in scan_results.items():
            for (cycle, score) in res["ranked_cycles"]:
                cluster.setdefault(cycle, []).append((sym, score))

        # Sort each cluster
        for cycle, lst in cluster.items():
            cluster[cycle] = sorted(lst, key=lambda x: x[1], reverse=True)

        return cluster

    # ---------------------------------------------------------------
    # Export CSV summary
    # ---------------------------------------------------------------
    def export_csv(self, scan_results, path="cycle_scan_report.csv"):
        """
        Export scan results to CSV.
        
        Args:
            scan_results: Results from scan()
            path: Output CSV path
        
        Returns:
            DataFrame with results
        """
        rows = []
        for sym, res in scan_results.items():
            for cycle, score in res["ranked_cycles"]:
                rows.append([sym, cycle, score])

        df = pd.DataFrame(rows, columns=["Symbol", "Cycle", "Score"])
        df.to_csv(path, index=False)
        return df

