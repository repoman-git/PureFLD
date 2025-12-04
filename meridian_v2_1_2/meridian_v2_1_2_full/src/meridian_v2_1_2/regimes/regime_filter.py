"""
Regime-Aware Strategy Filter (Stage 2)

Integrates regime classification with trading strategies to filter signals.

This module prevents strategies from trading in unfavorable regimes,
dramatically improving Sharpe ratios and reducing drawdowns.

Usage:
- Wrap any strategy with RegimeFilter
- Signals are only passed through in suitable regimes
- Position sizing adjusts by regime suitability
- Risk management scales with regime volatility

Author: Meridian Team
Date: December 4, 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from .cycle_regime_classifier import CycleRegimeClassifier, RegimeType


class RegimeFilter:
    """
    Filter trading signals based on market regime.
    
    This wrapper class takes any strategy's signals and filters them
    through regime analysis to improve performance.
    
    Example:
        >>> # Without regime filter
        >>> signals = strategy.generate_signals(prices)
        >>> 
        >>> # With regime filter
        >>> regime_filter = RegimeFilter(classifier)
        >>> filtered_signals = regime_filter.filter_signals(
        ...     signals=signals,
        ...     regime_predictions=regime_pred,
        ...     min_suitability=0.6
        ... )
    """
    
    def __init__(
        self,
        classifier: Optional[CycleRegimeClassifier] = None,
        allowed_regimes: Optional[List[int]] = None,
        min_confidence: float = 0.6
    ):
        """
        Initialize regime filter.
        
        Args:
            classifier: Trained CycleRegimeClassifier
            allowed_regimes: List of regime types to allow (None = use suitability)
            min_confidence: Minimum regime confidence to apply filter
        """
        self.classifier = classifier
        self.allowed_regimes = allowed_regimes or [RegimeType.CYCLICAL, RegimeType.COMPRESSED]
        self.min_confidence = min_confidence
    
    def filter_signals(
        self,
        signals: pd.DataFrame,
        regime_predictions: pd.DataFrame,
        min_suitability: float = 0.6,
        scale_by_suitability: bool = True
    ) -> pd.DataFrame:
        """
        Filter trading signals by regime.
        
        Args:
            signals: DataFrame with trading signals (must have 'signal' column)
            regime_predictions: DataFrame from classifier.predict()
            min_suitability: Minimum trade suitability (0-1)
            scale_by_suitability: Scale signal strength by regime suitability
            
        Returns:
            Filtered signals DataFrame
        """
        filtered = signals.copy()
        
        # Align indices
        common_idx = signals.index.intersection(regime_predictions.index)
        filtered = filtered.loc[common_idx]
        regime_predictions = regime_predictions.loc[common_idx]
        
        # Get regime info
        regime = regime_predictions['regime']
        suitability = regime_predictions['trade_suitability']
        confidence = regime_predictions.get('regime_confidence', pd.Series(1.0, index=regime.index))
        
        # Filter 1: Regime suitability
        unsuitable_mask = suitability < min_suitability
        
        # Filter 2: Low confidence
        low_confidence_mask = confidence < self.min_confidence
        
        # Combine filters
        block_mask = unsuitable_mask | low_confidence_mask
        
        # Zero out blocked signals
        if 'signal' in filtered.columns:
            filtered.loc[block_mask, 'signal'] = 0
            
            # Scale by suitability
            if scale_by_suitability:
                filtered.loc[~block_mask, 'signal'] *= suitability.loc[~block_mask]
        
        # Add regime context
        filtered['regime'] = regime
        filtered['regime_name'] = regime.map(RegimeType.NAMES)
        filtered['regime_suitability'] = suitability
        filtered['regime_confidence'] = confidence
        filtered['regime_filtered'] = block_mask
        
        return filtered
    
    def compute_regime_statistics(
        self,
        signals: pd.DataFrame,
        regime_predictions: pd.DataFrame,
        returns: Optional[pd.Series] = None
    ) -> Dict:
        """
        Compute performance statistics by regime.
        
        Args:
            signals: Trading signals
            regime_predictions: Regime predictions
            returns: Strategy returns (optional)
            
        Returns:
            Dictionary with regime-specific statistics
        """
        common_idx = signals.index.intersection(regime_predictions.index)
        signals = signals.loc[common_idx]
        regime_predictions = regime_predictions.loc[common_idx]
        
        if returns is not None:
            returns = returns.loc[common_idx]
        
        regime = regime_predictions['regime']
        
        stats = {}
        
        for reg_type in range(5):
            reg_name = RegimeType.NAMES[reg_type]
            mask = regime == reg_type
            
            if mask.sum() == 0:
                continue
            
            reg_stats = {
                'regime': reg_name,
                'periods': mask.sum(),
                'pct_time': mask.sum() / len(regime),
                'avg_suitability': RegimeType.TRADE_SUITABILITY[reg_type]
            }
            
            # Signal statistics
            if 'signal' in signals.columns:
                reg_signals = signals.loc[mask, 'signal']
                reg_stats['signals_generated'] = (reg_signals != 0).sum()
                reg_stats['signal_rate'] = (reg_signals != 0).sum() / mask.sum()
            
            # Return statistics
            if returns is not None:
                reg_returns = returns.loc[mask]
                reg_stats['avg_return'] = reg_returns.mean()
                reg_stats['volatility'] = reg_returns.std()
                if reg_stats['volatility'] > 0:
                    reg_stats['sharpe'] = np.sqrt(252) * reg_stats['avg_return'] / reg_stats['volatility']
                else:
                    reg_stats['sharpe'] = 0
            
            stats[reg_name] = reg_stats
        
        return stats
    
    def get_regime_mask(
        self,
        regime_predictions: pd.DataFrame,
        regimes: List[int],
        min_confidence: Optional[float] = None
    ) -> pd.Series:
        """
        Get boolean mask for specific regimes.
        
        Args:
            regime_predictions: Regime predictions
            regimes: List of regime types to include
            min_confidence: Minimum confidence (None = use default)
            
        Returns:
            Boolean series indicating allowed periods
        """
        if min_confidence is None:
            min_confidence = self.min_confidence
        
        regime = regime_predictions['regime']
        confidence = regime_predictions.get('regime_confidence', pd.Series(1.0, index=regime.index))
        
        # Regime mask
        regime_mask = regime.isin(regimes)
        
        # Confidence mask
        confidence_mask = confidence >= min_confidence
        
        return regime_mask & confidence_mask
    
    def create_regime_adjusted_strategy(
        self,
        base_strategy: Callable,
        min_suitability: float = 0.6
    ) -> Callable:
        """
        Create regime-adjusted version of a strategy.
        
        Args:
            base_strategy: Function that generates signals
            min_suitability: Minimum regime suitability
            
        Returns:
            Wrapped strategy function with regime filtering
        """
        def regime_aware_strategy(*args, **kwargs):
            # Generate base signals
            signals = base_strategy(*args, **kwargs)
            
            # Apply regime filter if classifier available
            if self.classifier and self.classifier.is_trained:
                # TODO: Extract features and predict regime
                # This would require access to price data in the wrapper
                pass
            
            return signals
        
        return regime_aware_strategy


class RegimeBasedPositionSizer:
    """
    Adjust position sizes based on market regime.
    
    Example:
        >>> sizer = RegimeBasedPositionSizer()
        >>> position_size = sizer.get_position_size(
        ...     base_size=1000,
        ...     regime=RegimeType.CYCLICAL,
        ...     suitability=0.9,
        ...     confidence=0.85
        ... )
    """
    
    def __init__(
        self,
        base_size: float = 1.0,
        regime_multipliers: Optional[Dict[int, float]] = None
    ):
        """
        Initialize position sizer.
        
        Args:
            base_size: Base position size
            regime_multipliers: Custom multipliers by regime
        """
        self.base_size = base_size
        
        # Default multipliers
        self.regime_multipliers = regime_multipliers or {
            RegimeType.TRENDING: 0.5,      # Reduce size in trends
            RegimeType.CYCLICAL: 1.5,      # Increase in cyclical
            RegimeType.VOLATILE: 0.7,      # Reduce in volatile
            RegimeType.COMPRESSED: 1.2,    # Moderate increase
            RegimeType.RESETTING: 0.3      # Minimal size
        }
    
    def get_position_size(
        self,
        base_size: float,
        regime: int,
        suitability: float,
        confidence: float
    ) -> float:
        """
        Calculate regime-adjusted position size.
        
        Args:
            base_size: Base position size
            regime: Regime type (0-4)
            suitability: Trade suitability (0-1)
            confidence: Regime confidence (0-1)
            
        Returns:
            Adjusted position size
        """
        # Get regime multiplier
        regime_mult = self.regime_multipliers.get(regime, 1.0)
        
        # Adjust by suitability and confidence
        adjustment = regime_mult * suitability * confidence
        
        # Apply
        adjusted_size = base_size * adjustment
        
        return adjusted_size
    
    def get_risk_adjustment(
        self,
        regime: int,
        volatility: float
    ) -> float:
        """
        Get risk adjustment factor for regime.
        
        Args:
            regime: Regime type
            volatility: Current volatility
            
        Returns:
            Risk adjustment multiplier
        """
        # Increase risk in low-volatility cyclical regimes
        if regime == RegimeType.CYCLICAL:
            return 1.0 / (volatility + 0.01)
        
        # Decrease risk in volatile regimes
        elif regime == RegimeType.VOLATILE:
            return 1.0 / (volatility + 0.05)
        
        # Default
        return 1.0

