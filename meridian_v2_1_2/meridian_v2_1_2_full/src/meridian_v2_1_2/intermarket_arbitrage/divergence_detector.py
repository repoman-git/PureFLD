"""
Divergence Detector

Identifies when cycles diverge beyond normal bounds, creating trading opportunities.

Logic:
1. Track spread between normalized cycle phases
2. Detect when spread exceeds historical threshold
3. Identify cycle-confirmed divergence (both instruments at similar cycle phase)
4. Generate mean-reversion signals

Divergence Types:
- Price divergence: Prices move apart while cycles converge
- Cycle divergence: Cycles diverge while prices remain aligned
- Combined divergence: Both price and cycle diverge (strongest signal)

Signal Strength:
- Threshold breach (1-3 standard deviations)
- Cycle phase alignment
- Historical reversion rate
- Market regime filter

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from ..hurst.hurst_phasing import HurstPhasingEngine


class DivergenceType(Enum):
    """Type of divergence detected"""
    PRICE_DIVERGENCE = "price"
    CYCLE_DIVERGENCE = "cycle"
    COMBINED_DIVERGENCE = "combined"
    NO_DIVERGENCE = "none"


class DivergenceDirection(Enum):
    """Direction of divergence"""
    POSITIVE = 1   # Lead asset outperforming
    NEGATIVE = -1  # Lag asset outperforming
    NEUTRAL = 0


@dataclass
class DivergenceSignal:
    """Container for a divergence event"""
    timestamp: pd.Timestamp
    lead_asset: str
    lag_asset: str
    divergence_type: DivergenceType
    direction: DivergenceDirection
    magnitude: float  # In standard deviations
    spread_value: float
    spread_zscore: float
    cycle_phase_diff: float
    confidence: float  # 0-1
    
    def __repr__(self):
        return (f"DivergenceSignal({self.lead_asset}/{self.lag_asset}, "
                f"type={self.divergence_type.value}, mag={self.magnitude:.2f}σ, "
                f"conf={self.confidence:.2f})")


class DivergenceDetector:
    """
    Detects cycle and price divergences between paired instruments.
    
    The detector monitors spread behavior and cycle phase alignment to identify:
    - Extreme spread values (mean reversion opportunities)
    - Cycle divergence (phase misalignment)
    - Combined signals (strongest opportunities)
    
    Example:
        >>> detector = DivergenceDetector(threshold_sigma=2.0)
        >>> 
        >>> signals = detector.detect_divergences(
        ...     lead_asset='GLD',
        ...     lag_asset='SLV',
        ...     lead_prices=gold_prices,
        ...     lag_prices=silver_prices,
        ...     lookback_days=252
        ... )
        >>> 
        >>> for signal in signals[-5:]:
        ...     print(signal)
    """
    
    def __init__(
        self,
        threshold_sigma: float = 2.0,
        lookback_days: int = 252,
        cycle_periods: List[int] = [20, 40, 80],
        min_confidence: float = 0.6
    ):
        """
        Initialize divergence detector.
        
        Args:
            threshold_sigma: Spread z-score threshold for signal
            lookback_days: Rolling window for spread statistics
            cycle_periods: Cycle periods to analyze
            min_confidence: Minimum confidence to generate signal
        """
        self.threshold_sigma = threshold_sigma
        self.lookback_days = lookback_days
        self.cycle_periods = cycle_periods
        self.min_confidence = min_confidence
        
        self.phasing_engine = HurstPhasingEngine()
    
    def detect_divergences(
        self,
        lead_asset: str,
        lag_asset: str,
        lead_prices: pd.Series,
        lag_prices: pd.Series,
        start_date: Optional[pd.Timestamp] = None,
        end_date: Optional[pd.Timestamp] = None
    ) -> List[DivergenceSignal]:
        """
        Detect all divergence events for a pair over time period.
        
        Args:
            lead_asset: Symbol of leading instrument
            lag_asset: Symbol of lagging instrument
            lead_prices: Price series for lead asset
            lag_prices: Price series for lag asset
            start_date: Start of detection period (None = full series)
            end_date: End of detection period (None = full series)
            
        Returns:
            List of DivergenceSignal objects
        """
        # Align price series
        common_idx = lead_prices.index.intersection(lag_prices.index)
        lead_prices = lead_prices.loc[common_idx]
        lag_prices = lag_prices.loc[common_idx]
        
        if start_date:
            lead_prices = lead_prices.loc[start_date:]
            lag_prices = lag_prices.loc[start_date:]
        if end_date:
            lead_prices = lead_prices.loc[:end_date]
            lag_prices = lag_prices.loc[:end_date]
        
        if len(lead_prices) < self.lookback_days:
            return []
        
        # Compute normalized spread
        spread = self._compute_spread(lead_prices, lag_prices)
        
        # Compute rolling statistics
        spread_mean = spread.rolling(self.lookback_days, min_periods=20).mean()
        spread_std = spread.rolling(self.lookback_days, min_periods=20).std()
        spread_zscore = (spread - spread_mean) / spread_std
        
        # Compute cycle phases
        lead_phases = self._compute_average_phase(lead_prices)
        lag_phases = self._compute_average_phase(lag_prices)
        
        # Detect divergence events
        signals = []
        
        for i in range(self.lookback_days, len(spread)):
            timestamp = spread.index[i]
            
            # Skip if insufficient data
            if pd.isna(spread_zscore.iloc[i]):
                continue
            
            # Check for threshold breach
            zscore = spread_zscore.iloc[i]
            
            if abs(zscore) >= self.threshold_sigma:
                signal = self._analyze_divergence_point(
                    timestamp=timestamp,
                    lead_asset=lead_asset,
                    lag_asset=lag_asset,
                    spread_value=spread.iloc[i],
                    spread_zscore=zscore,
                    lead_phase=lead_phases.iloc[i] if i < len(lead_phases) else 0,
                    lag_phase=lag_phases.iloc[i] if i < len(lag_phases) else 0,
                    spread_history=spread.iloc[max(0, i-20):i]
                )
                
                if signal and signal.confidence >= self.min_confidence:
                    signals.append(signal)
        
        return signals
    
    def get_current_divergence(
        self,
        lead_asset: str,
        lag_asset: str,
        lead_prices: pd.Series,
        lag_prices: pd.Series
    ) -> Optional[DivergenceSignal]:
        """
        Get current divergence status (most recent point).
        
        Returns:
            DivergenceSignal if divergence exists, None otherwise
        """
        signals = self.detect_divergences(
            lead_asset=lead_asset,
            lag_asset=lag_asset,
            lead_prices=lead_prices,
            lag_prices=lag_prices
        )
        
        if signals:
            return signals[-1]
        return None
    
    def _compute_spread(
        self,
        lead_prices: pd.Series,
        lag_prices: pd.Series
    ) -> pd.Series:
        """
        Compute normalized spread between two price series.
        """
        # Normalize both to start at 100
        norm_lead = 100 * lead_prices / lead_prices.iloc[0]
        norm_lag = 100 * lag_prices / lag_prices.iloc[0]
        
        # Spread is difference
        spread = norm_lead - norm_lag
        
        return spread
    
    def _compute_average_phase(self, prices: pd.Series) -> pd.Series:
        """
        Compute average cycle phase across all periods.
        
        Returns:
            Series with average phase (0-1)
        """
        phases = []
        
        for period in self.cycle_periods:
            try:
                result = self.phasing_engine.compute_phase(prices, period)
                phase = result.get('phase', pd.Series(0, index=prices.index))
                phases.append(phase)
            except Exception:
                phases.append(pd.Series(0, index=prices.index))
        
        if phases:
            avg_phase = pd.concat(phases, axis=1).mean(axis=1)
        else:
            avg_phase = pd.Series(0, index=prices.index)
        
        return avg_phase
    
    def _analyze_divergence_point(
        self,
        timestamp: pd.Timestamp,
        lead_asset: str,
        lag_asset: str,
        spread_value: float,
        spread_zscore: float,
        lead_phase: float,
        lag_phase: float,
        spread_history: pd.Series
    ) -> Optional[DivergenceSignal]:
        """
        Analyze a single divergence point to determine type and confidence.
        """
        # Compute phase difference
        phase_diff = abs(lead_phase - lag_phase)
        
        # Normalize phase difference to [0, 0.5]
        if phase_diff > 0.5:
            phase_diff = 1.0 - phase_diff
        
        # Determine divergence type
        price_diverged = abs(spread_zscore) >= self.threshold_sigma
        cycle_diverged = phase_diff >= 0.15  # 15% of cycle out of sync
        
        if price_diverged and cycle_diverged:
            div_type = DivergenceType.COMBINED_DIVERGENCE
        elif price_diverged:
            div_type = DivergenceType.PRICE_DIVERGENCE
        elif cycle_diverged:
            div_type = DivergenceType.CYCLE_DIVERGENCE
        else:
            div_type = DivergenceType.NO_DIVERGENCE
        
        # Determine direction
        if spread_zscore > 0:
            direction = DivergenceDirection.POSITIVE
        elif spread_zscore < 0:
            direction = DivergenceDirection.NEGATIVE
        else:
            direction = DivergenceDirection.NEUTRAL
        
        # Compute magnitude
        magnitude = abs(spread_zscore)
        
        # Compute confidence
        confidence = self._compute_confidence(
            div_type=div_type,
            magnitude=magnitude,
            phase_diff=phase_diff,
            spread_history=spread_history
        )
        
        return DivergenceSignal(
            timestamp=timestamp,
            lead_asset=lead_asset,
            lag_asset=lag_asset,
            divergence_type=div_type,
            direction=direction,
            magnitude=magnitude,
            spread_value=spread_value,
            spread_zscore=spread_zscore,
            cycle_phase_diff=phase_diff,
            confidence=confidence
        )
    
    def _compute_confidence(
        self,
        div_type: DivergenceType,
        magnitude: float,
        phase_diff: float,
        spread_history: pd.Series
    ) -> float:
        """
        Compute confidence score for divergence signal.
        
        Factors:
        - Divergence type (combined = highest)
        - Magnitude (higher = more confident)
        - Phase alignment (lower diff = higher confidence for price div)
        - Spread momentum (consistent direction = higher confidence)
        
        Returns:
            Confidence score 0-1
        """
        # Base score by type
        type_scores = {
            DivergenceType.COMBINED_DIVERGENCE: 0.9,
            DivergenceType.PRICE_DIVERGENCE: 0.7,
            DivergenceType.CYCLE_DIVERGENCE: 0.6,
            DivergenceType.NO_DIVERGENCE: 0.0
        }
        base_score = type_scores.get(div_type, 0.0)
        
        # Magnitude bonus (capped at 1.0)
        mag_bonus = min(0.3, (magnitude - self.threshold_sigma) * 0.1)
        
        # Phase alignment bonus (for price divergence)
        if div_type == DivergenceType.PRICE_DIVERGENCE:
            phase_bonus = max(0, 0.2 * (1.0 - phase_diff / 0.5))
        else:
            phase_bonus = 0
        
        # Momentum consistency check
        if len(spread_history) >= 5:
            recent_trend = np.sign(spread_history.iloc[-5:].diff().dropna())
            consistency = abs(recent_trend.mean())
            momentum_bonus = 0.1 * consistency
        else:
            momentum_bonus = 0
        
        # Combine scores
        confidence = min(1.0, base_score + mag_bonus + phase_bonus + momentum_bonus)
        
        return confidence
    
    def plot_divergence_history(
        self,
        lead_asset: str,
        lag_asset: str,
        lead_prices: pd.Series,
        lag_prices: pd.Series,
        signals: Optional[List[DivergenceSignal]] = None
    ) -> Dict:
        """
        Generate plot data for divergence history visualization.
        
        Returns:
            Dictionary with plot data
        """
        if signals is None:
            signals = self.detect_divergences(
                lead_asset, lag_asset, lead_prices, lag_prices
            )
        
        # Compute spread
        common_idx = lead_prices.index.intersection(lag_prices.index)
        lead_prices = lead_prices.loc[common_idx]
        lag_prices = lag_prices.loc[common_idx]
        spread = self._compute_spread(lead_prices, lag_prices)
        
        # Compute rolling statistics
        spread_mean = spread.rolling(self.lookback_days, min_periods=20).mean()
        spread_std = spread.rolling(self.lookback_days, min_periods=20).std()
        spread_zscore = (spread - spread_mean) / spread_std
        
        # Extract signal points
        signal_dates = [s.timestamp for s in signals]
        signal_values = [s.spread_zscore for s in signals]
        signal_types = [s.divergence_type.value for s in signals]
        
        return {
            'dates': spread.index,
            'spread': spread.values,
            'spread_zscore': spread_zscore.values,
            'upper_threshold': self.threshold_sigma,
            'lower_threshold': -self.threshold_sigma,
            'signal_dates': signal_dates,
            'signal_values': signal_values,
            'signal_types': signal_types,
            'lead_asset': lead_asset,
            'lag_asset': lag_asset
        }

