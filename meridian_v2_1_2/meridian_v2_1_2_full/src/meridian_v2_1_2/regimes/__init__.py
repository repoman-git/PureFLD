"""
Regime Classification Module for Meridian v2.1.2

Market structure intelligence through volatility, trend, and cycle regime detection.
"""

from .volatility import classify_volatility
from .trend import classify_trend
from .cycles import classify_cycle_regime
from .composite import compute_composite_regime
from .regime_utils import normalize_regime, smooth_regime

__all__ = [
    'classify_volatility',
    'classify_trend',
    'classify_cycle_regime',
    'compute_composite_regime',
    'normalize_regime',
    'smooth_regime',
]

