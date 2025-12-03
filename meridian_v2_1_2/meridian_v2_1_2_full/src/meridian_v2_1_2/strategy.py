import pandas as pd
from typing import Optional

from .config import StrategyConfig

class FLDStrategy:
    """FLD-based trading strategy with COT and TDOM filtering"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
    
    def generate_signals(
        self,
        prices: pd.Series,
        fld: pd.Series,
        cot_series: Optional[pd.Series] = None,
        seasonal_score: Optional[pd.Series] = None,
        tdom_series: Optional[pd.Series] = None,  # Deprecated, use seasonal_score
        cycle_phase: Optional[pd.Series] = None,
        cycle_amplitude: Optional[pd.Series] = None,
        cycle_score: Optional[pd.Series] = None,
        turning_points: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """
        Generate trading signals from FLD crossovers with optional filters.
        
        Args:
            prices: Price series
            fld: FLD line series
            cot_series: Optional COT factor series for filtering
            seasonal_score: Optional seasonal score (-2 to +2) from TDOM/TDOY
            tdom_series: DEPRECATED - use seasonal_score instead
            cycle_phase: Optional normalized cycle phase (0.0 to 1.0)
            cycle_amplitude: Optional cycle amplitude series
            cycle_score: Optional cycle quality score (-1 to +1)
            turning_points: Optional turning point series (+1/-1/0)
        
        Returns:
            DataFrame with columns: ['signal', 'position']
            signal: 1=long, -1=short, 0=flat
            position: running position after applying signal
            
        Raises:
            ValueError: If any series indices don't match price index
        """
        # Backward compatibility: if tdom_series provided but not seasonal_score, use it
        if seasonal_score is None and tdom_series is not None:
            seasonal_score = tdom_series
        
        # Validate indices
        if cot_series is not None and not prices.index.equals(cot_series.index):
            raise ValueError("COT series index does not match price series index.")
        if seasonal_score is not None and not prices.index.equals(seasonal_score.index):
            raise ValueError("Seasonal score index does not match price series index.")
        if cycle_phase is not None and not prices.index.equals(cycle_phase.index):
            raise ValueError("Cycle phase index does not match price series index.")
        if cycle_score is not None and not prices.index.equals(cycle_score.index):
            raise ValueError("Cycle score index does not match price series index.")
        # Basic FLD crossover signals
        cross_above = (prices > fld) & (prices.shift(1) <= fld.shift(1))
        cross_below = (prices < fld) & (prices.shift(1) >= fld.shift(1))
        
        signals = pd.Series(0, index=prices.index)
        signals[cross_above] = 1
        signals[cross_below] = -1
        
        # Apply seasonal gating (TDOM + TDOY combined)
        if (self.config.use_tdom or hasattr(self.config, 'use_tdoy')) and seasonal_score is not None:
            # Block entries when seasonal_score < 0 (unfavourable conditions)
            blocked = (seasonal_score < 0)
            signals[blocked] = 0
        
        # Apply COT filtering
        if self.config.use_cot and cot_series is not None:
            # Block longs when COT < long_threshold
            # Block shorts when COT > short_threshold
            block_longs = cot_series < self.config.cot_long_threshold
            block_shorts = cot_series > self.config.cot_short_threshold
            signals[(signals == 1) & block_longs] = 0
            signals[(signals == -1) & block_shorts] = 0
        
        # Apply cycle-based filters
        if self.config.cycle_strategy.enable_cycle_filters:
            signals = self._apply_cycle_filters(
                signals, cycle_phase, cycle_amplitude, cycle_score, turning_points
            )
        
        # Disable shorts if not allowed
        if not self.config.allow_shorts:
            signals[signals == -1] = 0
        
        # Convert signals to positions (forward fill non-zero signals)
        # Apply contracts multiplier
        positions = pd.Series(0, index=signals.index, dtype=int)
        current_pos = 0
        for i, sig in enumerate(signals):
            if sig != 0:
                current_pos = sig * self.config.contracts
            positions.iloc[i] = current_pos
        
        return pd.DataFrame({
            'signal': signals,
            'position': positions
        }, index=prices.index)
    
    def _apply_cycle_filters(
        self,
        signals: pd.Series,
        cycle_phase: Optional[pd.Series],
        cycle_amplitude: Optional[pd.Series],
        cycle_score: Optional[pd.Series],
        turning_points: Optional[pd.Series]
    ) -> pd.Series:
        """
        Apply cycle-based filters to signals.
        
        Returns:
            pd.Series: Filtered signals
        """
        filtered = signals.copy()
        cycle_cfg = self.config.cycle_strategy
        
        # 1. Phase Range Filter
        if cycle_phase is not None and len(cycle_cfg.allowed_phase_ranges) > 0:
            # Check if current phase is in any allowed range
            phase_allowed = pd.Series(False, index=signals.index)
            
            for phase_min, phase_max in cycle_cfg.allowed_phase_ranges:
                in_range = (cycle_phase >= phase_min) & (cycle_phase <= phase_max)
                phase_allowed = phase_allowed | in_range
            
            # Block signals outside allowed phases
            filtered[~phase_allowed] = 0
        
        # 2. Turning Point Alignment
        if cycle_cfg.require_turning_point_alignment and turning_points is not None:
            # Check if there's a turning point within max_bars
            max_bars = cycle_cfg.max_bars_from_turning_point
            
            tp_aligned = pd.Series(False, index=signals.index)
            
            for i in range(len(turning_points)):
                # Look within window
                start_idx = max(0, i - max_bars)
                end_idx = min(len(turning_points), i + max_bars + 1)
                
                window_tp = turning_points.iloc[start_idx:end_idx]
                
                # If any turning point in window, mark as aligned
                if (window_tp != 0).any():
                    tp_aligned.iloc[i] = True
            
            # Block signals not aligned with turning points
            filtered[~tp_aligned] = 0
        
        # 3. Minimum Amplitude
        if cycle_amplitude is not None and cycle_cfg.min_cycle_amplitude > 0:
            insufficient_amplitude = cycle_amplitude < cycle_cfg.min_cycle_amplitude
            filtered[insufficient_amplitude] = 0
        
        # 4. Cycle Score Threshold
        if cycle_score is not None and cycle_cfg.min_cycle_score > -999:
            low_score = cycle_score < cycle_cfg.min_cycle_score
            filtered[low_score] = 0
        
        return filtered
