"""
Portfolio Engine for Meridian v2.1.2

Multi-market execution with capital allocation, exposure control, and correlation management.
"""

from .portfolio_allocator import allocate_capital, compute_portfolio_weights
from .exposure_manager import compute_exposures, enforce_exposure_limits
from .correlation_manager import compute_correlation_matrix, manage_correlation_risk
from .portfolio_risk import compute_portfolio_volatility, target_portfolio_volatility
from .portfolio_utils import combine_positions, aggregate_pnl

__all__ = [
    'allocate_capital',
    'compute_portfolio_weights',
    'compute_exposures',
    'enforce_exposure_limits',
    'compute_correlation_matrix',
    'manage_correlation_risk',
    'compute_portfolio_volatility',
    'target_portfolio_volatility',
    'combine_positions',
    'aggregate_pnl',
]

