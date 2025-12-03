"""
Storage Layer for Meridian v2.1.2

Handles persistent storage of backtest results, configurations, and run history.
"""

from .backtest_registry import (
    save_run,
    load_all_runs,
    load_run_by_id,
    delete_run,
    get_registry_stats
)

__all__ = [
    'save_run',
    'load_all_runs',
    'load_run_by_id',
    'delete_run',
    'get_registry_stats'
]
