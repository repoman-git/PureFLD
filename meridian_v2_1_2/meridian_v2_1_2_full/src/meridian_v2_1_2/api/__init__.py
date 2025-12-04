"""
API Layer for Meridian v2.1.2

Provides clean interfaces to core functionality for notebooks and dashboard.
"""

from .backtest_runner import run_backtest, BacktestResult

__all__ = ['run_backtest', 'BacktestResult']


