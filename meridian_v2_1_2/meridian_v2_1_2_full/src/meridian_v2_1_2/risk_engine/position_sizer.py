"""
Unified Position Sizer for Meridian v2.1.2

Combines all risk factors into final position sizes.
"""

import pandas as pd
from typing import Optional, Dict

from .risk_config import RiskConfig
from .volatility_risk import compute_volatility_sizing
from .regime_risk import apply_regime_multipliers
from .cycle_risk import apply_cycle_sizing
from .kelly_risk import apply_kelly_sizing
from .risk_caps import apply_risk_caps
from .risk_utils import smooth_sizes


def compute_position_sizes(
    prices: pd.Series,
    vol_regime: Optional[pd.Series],
    trend_regime: Optional[pd.Series],
    cycle_regime: Optional[pd.Series],
    cycle_amplitude: Optional[pd.Series],
    cycle_score: Optional[pd.Series],
    trade_stats: Optional[Dict],
    config: RiskConfig
) -> pd.Series:
    """
    Compute adaptive position sizes using all risk factors.
    
    Pipeline:
    1. Start with base size = 1.0
    2. Apply volatility sizing (if enabled)
    3. Apply regime multipliers (if enabled)
    4. Apply cycle sizing (if enabled)
    5. Apply Kelly fraction (if enabled)
    6. Apply hard risk caps
    7. Smooth final sizes
    
    Args:
        prices: Price series
        vol_regime: Volatility regime series
        trend_regime: Trend regime series
        cycle_regime: Cycle regime series
        cycle_amplitude: Cycle amplitude series
        cycle_score: Cycle score series
        trade_stats: Trade statistics for Kelly
        config: Risk configuration
    
    Returns:
        pd.Series: Final position sizes
    
    Notes:
        - Each factor multiplies the size
        - All factors are optional
        - Hard caps always applied
        - Deterministic calculation
    """
    # Start with base size
    sizes = pd.Series(1.0, index=prices.index)
    
    # 1. Volatility sizing
    if config.use_volatility_sizing:
        vol_sizes = compute_volatility_sizing(prices, config)
        sizes *= vol_sizes
    
    # 2. Regime multipliers
    if config.use_regime_sizing and vol_regime is not None and trend_regime is not None and cycle_regime is not None:
        sizes = apply_regime_multipliers(sizes, vol_regime, trend_regime, cycle_regime, config)
    
    # 3. Cycle sizing
    if config.use_cycle_sizing and cycle_amplitude is not None and cycle_score is not None:
        sizes = apply_cycle_sizing(sizes, cycle_amplitude, cycle_score, config)
    
    # 4. Kelly sizing
    if config.use_kelly and trade_stats is not None:
        sizes = apply_kelly_sizing(sizes, trade_stats, config)
    
    # 5. Apply hard caps
    sizes = apply_risk_caps(sizes, config)
    
    # 6. Smooth final sizes
    if config.smoothing_window > 1:
        sizes = smooth_sizes(sizes, config.smoothing_window)
    
    sizes.name = 'position_size'
    return sizes


