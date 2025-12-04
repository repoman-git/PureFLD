"""
Regime Classification Module for Meridian v2.1.2

Market structure intelligence through volatility, trend, and cycle regime detection.

Stage 2 (NEW):
- ML-powered cycle regime classifier
- Regime-aware strategy filtering
- Interactive dashboard

Legacy modules:
- Basic volatility, trend, and cycle classification
"""

# Legacy modules
from .volatility import classify_volatility
from .trend import classify_trend
from .cycles import classify_cycle_regime
from .composite import compute_composite_regime
from .regime_utils import normalize_regime, smooth_regime

# Stage 2: ML-powered regime classification
from .cycle_regime_classifier import CycleRegimeClassifier, RegimeType
from .regime_filter import RegimeFilter, RegimeBasedPositionSizer

# Optional: Dashboard (requires streamlit)
try:
    from .regime_dashboard import RegimeDashboard, run_regime_dashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    RegimeDashboard = None
    run_regime_dashboard = None
    _DASHBOARD_AVAILABLE = False

__all__ = [
    # Legacy
    'classify_volatility',
    'classify_trend',
    'classify_cycle_regime',
    'compute_composite_regime',
    'normalize_regime',
    'smooth_regime',
    # Stage 2
    'CycleRegimeClassifier',
    'RegimeType',
    'RegimeFilter',
    'RegimeBasedPositionSizer',
    'RegimeDashboard',
    'run_regime_dashboard',
]


