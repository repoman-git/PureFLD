"""
Portfolio Allocation Engine (Stage 3)

Cycle-aware portfolio optimization and capital allocation.

This module converts cycle intelligence into optimal position sizes and portfolio weights.
It combines insights from Stages 1 & 2 (pairs trading + regime classification) with
sophisticated risk management and cycle-based weighting.

Features:
- Cycle-aware feature extraction
- Risk modeling with regime integration
- Cycle strength weighting
- Multi-asset portfolio optimization
- Portfolio backtesting
- Interactive visualization

This is institutional-grade portfolio management.

Author: Meridian Team
Date: December 4, 2025
Stage: 3 of 10
"""

from .feature_builder import PortfolioFeatureBuilder
from .risk_model import PortfolioRiskModel
from .cycle_weighting import CycleWeightingModel
from .allocation_core import PortfolioAllocator
from .optimizer import AllocationOptimizer
from .portfolio_backtest import PortfolioBacktestEngine

# Optional: Dashboard (requires streamlit)
try:
    from .portfolio_dashboard import plot_portfolio_dashboard, PortfolioDashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    plot_portfolio_dashboard = None
    PortfolioDashboard = None
    _DASHBOARD_AVAILABLE = False

__all__ = [
    'PortfolioFeatureBuilder',
    'PortfolioRiskModel',
    'CycleWeightingModel',
    'PortfolioAllocator',
    'AllocationOptimizer',
    'PortfolioBacktestEngine',
    'plot_portfolio_dashboard',
    'PortfolioDashboard',
]

__version__ = '1.0.0'

