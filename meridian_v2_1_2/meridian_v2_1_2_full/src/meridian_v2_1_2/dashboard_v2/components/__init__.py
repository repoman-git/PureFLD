"""
Dashboard v2 UI Components

Self-contained renderers for multi-strategy views.
"""

from .portfolio_overview import PortfolioOverview
from .strategy_cards import StrategyCards
from .strategy_comparison import StrategyComparison
from .allocation_panel import AllocationPanel
from .combined_pnl import CombinedPnL
from .correlation_map import CorrelationMap
from .multi_approvals import MultiApprovals
from .portfolio_heatmap import PortfolioHeatmap

__all__ = [
    'PortfolioOverview',
    'StrategyCards',
    'StrategyComparison',
    'AllocationPanel',
    'CombinedPnL',
    'CorrelationMap',
    'MultiApprovals',
    'PortfolioHeatmap',
]

