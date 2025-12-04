"""
Volatility & Risk Engine (Stage 4)

Institutional-grade volatility modeling and dynamic risk management.

This module provides cycle-aware volatility analysis and dynamic stop-loss
distances, essential for live trading and risk management.

Features:
- Cycle-Aware ATR (C-ATR)
- Volatility envelopes (compression/expansion detection)
- Cycle-driven volatility modeling
- Turning-point volatility spike detection
- Risk Window Score (RWS)
- Dynamic stop distances
- Interactive visualization

This is the risk layer that separates retail from institutional.

Author: Meridian Team
Date: December 4, 2025
Stage: 4 of 10
"""

from .vol_feature_builder import VolFeatureBuilder
from .cycle_atr import CycleATR
from .vol_envelope import VolatilityEnvelope
from .cycle_vol_model import CycleVolatilityModel
from .risk_window import RiskWindowModel
from .stop_model import StopDistanceModel

# Optional: Dashboard
try:
    from .dashboard import plot_volatility_dashboard, VolatilityDashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    plot_volatility_dashboard = None
    VolatilityDashboard = None
    _DASHBOARD_AVAILABLE = False

__all__ = [
    'VolFeatureBuilder',
    'CycleATR',
    'VolatilityEnvelope',
    'CycleVolatilityModel',
    'RiskWindowModel',
    'StopDistanceModel',
    'plot_volatility_dashboard',
    'VolatilityDashboard',
]

__version__ = '1.0.0'

