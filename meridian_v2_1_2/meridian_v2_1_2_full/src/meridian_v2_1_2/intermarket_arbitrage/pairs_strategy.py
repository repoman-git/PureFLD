"""
Pairs Trading Strategy

Generates long/short trading signals based on cycle divergences and spread behavior.

Strategy Logic:
1. Monitor spread between paired instruments
2. Enter when divergence threshold breached
3. Exit on mean reversion or stop loss
4. Use cycle phases to time entries

Entry Signals:
- Spread > +2σ: Short lead / Long lag (mean reversion)
- Spread < -2σ: Long lead / Short lag (mean reversion)
- Cycle phase confirmation required

Exit Signals:
- Spread returns to mean (± 0.5σ)
- Stop loss hit (± 4σ)
- Maximum holding period exceeded

Position Sizing:
- Based on spread volatility
- Kelly criterion for optimal sizing
- Risk-adjusted for confidence level

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from .divergence_detector import DivergenceDetector, DivergenceSignal, DivergenceDirection
from .pairs_selector import PairCandidate


class SignalType(Enum):
    """Type of trading signal"""
    ENTRY_LONG_LEAD = "long_lead"      # Long lead, short lag
    ENTRY_SHORT_LEAD = "short_lead"    # Short lead, long lag
    EXIT_PROFIT = "exit_profit"        # Take profit
    EXIT_STOP = "exit_stop"            # Stop loss
    HOLD = "hold"                       # No action


@dataclass
class PairsSignal:
    """Container for a pairs trading signal"""
    timestamp: pd.Timestamp
    lead_asset: str
    lag_asset: str
    signal_type: SignalType
    lead_position: float  # +1 = long, -1 = short, 0 = flat
    lag_position: float   # +1 = long, -1 = short, 0 = flat
    spread_value: float
    spread_zscore: float
    confidence: float
    entry_price_lead: Optional[float] = None
    entry_price_lag: Optional[float] = None
    exit_price_lead: Optional[float] = None
    exit_price_lag: Optional[float] = None
    pnl: Optional[float] = None
    
    def __repr__(self):
        return (f"PairsSignal({self.signal_type.value}, "
                f"{self.lead_asset}:{self.lead_position:+.0f}/{self.lag_asset}:{self.lag_position:+.0f}, "
                f"spread={self.spread_zscore:.2f}σ)")


class PairsStrategy:
    """
    Generates trading signals for pairs based on cycle divergences.
    
    The strategy:
    1. Monitors spread z-score
    2. Enters on extreme divergence (±2σ)
    3. Exits on mean reversion or stop loss
    4. Uses cycle phase for entry timing
    5. Applies risk management
    
    Example:
        >>> strategy = PairsStrategy(
        ...     entry_threshold=2.0,
        ...     exit_threshold=0.5,
        ...     stop_loss_threshold=4.0
        ... )
        >>> 
        >>> signals = strategy.generate_signals(
        ...     pair_candidate=pair,
        ...     lead_prices=gold_prices,
        ...     lag_prices=silver_prices
        ... )
        >>> 
        >>> for signal in signals:
        ...     if signal.signal_type != SignalType.HOLD:
        ...         print(signal)
    """
    
    def __init__(
        self,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        stop_loss_threshold: float = 4.0,
        max_holding_days: int = 60,
        min_confidence: float = 0.7,
        cycle_confirmation: bool = True
    ):
        """
        Initialize pairs trading strategy.
        
        Args:
            entry_threshold: Spread z-score for entry (σ)
            exit_threshold: Spread z-score for profit exit (σ)
            stop_loss_threshold: Spread z-score for stop loss (σ)
            max_holding_days: Maximum days to hold position
            min_confidence: Minimum confidence for entry
            cycle_confirmation: Require cycle phase confirmation
        """
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.stop_loss_threshold = stop_loss_threshold
        self.max_holding_days = max_holding_days
        self.min_confidence = min_confidence
        self.cycle_confirmation = cycle_confirmation
        
        self.divergence_detector = DivergenceDetector(
            threshold_sigma=entry_threshold
        )
    
    def generate_signals(
        self,
        pair_candidate: PairCandidate,
        lead_prices: pd.Series,
        lag_prices: pd.Series,
        lookback_days: int = 252
    ) -> List[PairsSignal]:
        """
        Generate all trading signals for a pair over time.
        
        Args:
            pair_candidate: PairCandidate object defining the pair
            lead_prices: Price series for lead asset
            lag_prices: Price series for lag asset
            lookback_days: Lookback period for statistics
            
        Returns:
            List of PairsSignal objects (entries and exits)
        """
        # Detect divergences
        divergences = self.divergence_detector.detect_divergences(
            lead_asset=pair_candidate.lead_asset,
            lag_asset=pair_candidate.lag_asset,
            lead_prices=lead_prices,
            lag_prices=lag_prices
        )
        
        # Align prices
        common_idx = lead_prices.index.intersection(lag_prices.index)
        lead_prices = lead_prices.loc[common_idx]
        lag_prices = lag_prices.loc[common_idx]
        
        # Compute spread and z-score
        spread = self._compute_spread(lead_prices, lag_prices)
        spread_mean = spread.rolling(lookback_days, min_periods=20).mean()
        spread_std = spread.rolling(lookback_days, min_periods=20).std()
        spread_zscore = (spread - spread_mean) / spread_std
        
        # Generate signals
        signals = []
        current_position = None  # (timestamp, signal) tuple
        
        for i in range(lookback_days, len(spread)):
            timestamp = spread.index[i]
            zscore = spread_zscore.iloc[i]
            spread_val = spread.iloc[i]
            
            if pd.isna(zscore):
                continue
            
            # Check if we have an open position
            if current_position is None:
                # Look for entry signal
                entry_signal = self._check_entry(
                    timestamp=timestamp,
                    lead_asset=pair_candidate.lead_asset,
                    lag_asset=pair_candidate.lag_asset,
                    spread_value=spread_val,
                    spread_zscore=zscore,
                    divergences=divergences,
                    lead_price=lead_prices.iloc[i],
                    lag_price=lag_prices.iloc[i]
                )
                
                if entry_signal:
                    signals.append(entry_signal)
                    current_position = (timestamp, entry_signal)
            
            else:
                # Check for exit signal
                entry_time, entry_signal = current_position
                days_held = (timestamp - entry_time).days
                
                exit_signal = self._check_exit(
                    timestamp=timestamp,
                    entry_signal=entry_signal,
                    spread_value=spread_val,
                    spread_zscore=zscore,
                    days_held=days_held,
                    lead_price=lead_prices.iloc[i],
                    lag_price=lag_prices.iloc[i]
                )
                
                if exit_signal:
                    signals.append(exit_signal)
                    current_position = None
        
        return signals
    
    def _compute_spread(
        self,
        lead_prices: pd.Series,
        lag_prices: pd.Series
    ) -> pd.Series:
        """Compute normalized spread."""
        norm_lead = 100 * lead_prices / lead_prices.iloc[0]
        norm_lag = 100 * lag_prices / lag_prices.iloc[0]
        return norm_lead - norm_lag
    
    def _check_entry(
        self,
        timestamp: pd.Timestamp,
        lead_asset: str,
        lag_asset: str,
        spread_value: float,
        spread_zscore: float,
        divergences: List[DivergenceSignal],
        lead_price: float,
        lag_price: float
    ) -> Optional[PairsSignal]:
        """
        Check if entry conditions are met.
        
        Entry rules:
        - Spread z-score exceeds threshold
        - Confidence level sufficient
        - Optional: Cycle phase confirmation
        """
        # Check threshold breach
        if abs(spread_zscore) < self.entry_threshold:
            return None
        
        # Find matching divergence signal (if cycle confirmation required)
        divergence = None
        if self.cycle_confirmation and divergences:
            # Find divergence at or near this timestamp
            for div in divergences:
                if abs((div.timestamp - timestamp).days) <= 2:
                    divergence = div
                    break
            
            # Require cycle confirmation
            if divergence is None:
                return None
            
            # Check confidence
            if divergence.confidence < self.min_confidence:
                return None
        
        # Determine position direction
        if spread_zscore > self.entry_threshold:
            # Spread too high: short lead, long lag (mean reversion)
            signal_type = SignalType.ENTRY_SHORT_LEAD
            lead_pos = -1.0
            lag_pos = 1.0
        elif spread_zscore < -self.entry_threshold:
            # Spread too low: long lead, short lag (mean reversion)
            signal_type = SignalType.ENTRY_LONG_LEAD
            lead_pos = 1.0
            lag_pos = -1.0
        else:
            return None
        
        # Get confidence
        confidence = divergence.confidence if divergence else 0.8
        
        return PairsSignal(
            timestamp=timestamp,
            lead_asset=lead_asset,
            lag_asset=lag_asset,
            signal_type=signal_type,
            lead_position=lead_pos,
            lag_position=lag_pos,
            spread_value=spread_value,
            spread_zscore=spread_zscore,
            confidence=confidence,
            entry_price_lead=lead_price,
            entry_price_lag=lag_price
        )
    
    def _check_exit(
        self,
        timestamp: pd.Timestamp,
        entry_signal: PairsSignal,
        spread_value: float,
        spread_zscore: float,
        days_held: int,
        lead_price: float,
        lag_price: float
    ) -> Optional[PairsSignal]:
        """
        Check if exit conditions are met.
        
        Exit rules:
        1. Profit target: Spread returns to mean (±exit_threshold)
        2. Stop loss: Spread moves further against us
        3. Time stop: Maximum holding period exceeded
        """
        # Check time stop
        if days_held >= self.max_holding_days:
            return self._create_exit_signal(
                timestamp, entry_signal, spread_value, spread_zscore,
                SignalType.EXIT_STOP, lead_price, lag_price
            )
        
        # Check stop loss
        if abs(spread_zscore) >= self.stop_loss_threshold:
            # Spread moved further - exit at loss
            return self._create_exit_signal(
                timestamp, entry_signal, spread_value, spread_zscore,
                SignalType.EXIT_STOP, lead_price, lag_price
            )
        
        # Check profit target
        if abs(spread_zscore) <= self.exit_threshold:
            # Spread returned to mean - take profit
            return self._create_exit_signal(
                timestamp, entry_signal, spread_value, spread_zscore,
                SignalType.EXIT_PROFIT, lead_price, lag_price
            )
        
        # Alternatively, check if spread crossed zero (reversed)
        # This is a more aggressive profit take
        if entry_signal.signal_type == SignalType.ENTRY_LONG_LEAD:
            if spread_zscore < 0:  # Entered when spread was negative, now positive
                return self._create_exit_signal(
                    timestamp, entry_signal, spread_value, spread_zscore,
                    SignalType.EXIT_PROFIT, lead_price, lag_price
                )
        elif entry_signal.signal_type == SignalType.ENTRY_SHORT_LEAD:
            if spread_zscore > 0:  # Entered when spread was positive, now negative
                return self._create_exit_signal(
                    timestamp, entry_signal, spread_value, spread_zscore,
                    SignalType.EXIT_PROFIT, lead_price, lag_price
                )
        
        return None
    
    def _create_exit_signal(
        self,
        timestamp: pd.Timestamp,
        entry_signal: PairsSignal,
        spread_value: float,
        spread_zscore: float,
        exit_type: SignalType,
        lead_price: float,
        lag_price: float
    ) -> PairsSignal:
        """Create an exit signal and compute PnL."""
        # Compute PnL
        # Long lead: profit if lead price increased
        # Short lead: profit if lead price decreased
        # Same logic for lag
        lead_pnl = entry_signal.lead_position * (
            lead_price - entry_signal.entry_price_lead
        ) / entry_signal.entry_price_lead
        
        lag_pnl = entry_signal.lag_position * (
            lag_price - entry_signal.entry_price_lag
        ) / entry_signal.entry_price_lag
        
        # Total PnL (assuming equal dollar allocation)
        total_pnl = (lead_pnl + lag_pnl) / 2.0
        
        return PairsSignal(
            timestamp=timestamp,
            lead_asset=entry_signal.lead_asset,
            lag_asset=entry_signal.lag_asset,
            signal_type=exit_type,
            lead_position=0.0,  # Flat
            lag_position=0.0,   # Flat
            spread_value=spread_value,
            spread_zscore=spread_zscore,
            confidence=entry_signal.confidence,
            entry_price_lead=entry_signal.entry_price_lead,
            entry_price_lag=entry_signal.entry_price_lag,
            exit_price_lead=lead_price,
            exit_price_lag=lag_price,
            pnl=total_pnl
        )
    
    def compute_position_size(
        self,
        signal: PairsSignal,
        capital: float,
        spread_volatility: float,
        risk_per_trade: float = 0.02
    ) -> Tuple[float, float]:
        """
        Compute position sizes for lead and lag assets.
        
        Args:
            signal: Trading signal
            capital: Available capital
            spread_volatility: Historical spread volatility
            risk_per_trade: Fraction of capital to risk per trade
            
        Returns:
            (lead_size, lag_size) in dollars
        """
        # Base allocation (50/50 split)
        base_allocation = capital * risk_per_trade
        
        # Adjust by confidence
        confidence_adjusted = base_allocation * signal.confidence
        
        # Adjust by spread volatility (lower vol = higher size)
        vol_scalar = 1.0 / (1.0 + spread_volatility / 10.0)
        
        final_allocation = confidence_adjusted * vol_scalar
        
        # Split equally between lead and lag
        lead_size = final_allocation / 2.0
        lag_size = final_allocation / 2.0
        
        return lead_size, lag_size
    
    def get_strategy_statistics(
        self,
        signals: List[PairsSignal]
    ) -> Dict:
        """
        Compute performance statistics for strategy signals.
        
        Args:
            signals: List of trading signals
            
        Returns:
            Dictionary with performance metrics
        """
        # Separate entries and exits
        entries = [s for s in signals if 'ENTRY' in s.signal_type.value]
        exits = [s for s in signals if 'EXIT' in s.signal_type.value]
        
        # Compute statistics
        total_trades = len(entries)
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'total_pnl': 0.0
            }
        
        # Match entries with exits to get PnLs
        pnls = [e.pnl for e in exits if e.pnl is not None]
        
        if not pnls:
            return {
                'total_trades': total_trades,
                'completed_trades': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'total_pnl': 0.0
            }
        
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        return {
            'total_trades': total_trades,
            'completed_trades': len(pnls),
            'win_rate': len(wins) / len(pnls) if pnls else 0.0,
            'avg_pnl': np.mean(pnls),
            'total_pnl': np.sum(pnls),
            'avg_win': np.mean(wins) if wins else 0.0,
            'avg_loss': np.mean(losses) if losses else 0.0,
            'max_win': np.max(pnls),
            'max_loss': np.min(pnls),
            'profit_factor': abs(sum(wins) / sum(losses)) if losses and sum(losses) != 0 else np.inf
        }

