"""
Intermarket Arbitrage Module

Cross-Market Arbitrage Engine for Meridian v2.1.2
Stage 1 of 10-Stage Roadmap

Converts cycle lead/lag relationships into actionable pairs trading strategies.

Features:
- Pairs selection based on cycle synchronization
- Divergence detection for mean-reversion opportunities
- Cycle-timed entry/exit signals
- Backtesting framework for pairs strategies
- Dashboard for monitoring pairs opportunities

Trading Logic:
- Long leader / Short lagger around cycle troughs
- Mean-reversion pairs around cycle peaks
- Divergence-based spread trading

Modules:
- pairs_selector: Select tradable pairs with high cycle correlation
- divergence_detector: Identify when cycles diverge beyond threshold
- pairs_strategy: Generate long/short signals from cycle lead/lag
- pairs_backtest: Backtest pairs strategies with realistic execution
- pairs_dashboard: Streamlit dashboard for pairs monitoring

Author: Meridian Team
Date: December 4, 2025
Status: Stage 1 Implementation
"""

from .pairs_selector import PairsSelector
from .divergence_detector import DivergenceDetector
from .pairs_strategy import PairsStrategy
from .pairs_backtest import PairsBacktester

# Optional: Import dashboard only if streamlit is available
try:
    from .pairs_dashboard import PairsDashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    PairsDashboard = None
    _DASHBOARD_AVAILABLE = False

__all__ = [
    'PairsSelector',
    'DivergenceDetector',
    'PairsStrategy',
    'PairsBacktester',
    'PairsDashboard',
]

__version__ = '1.0.0'

