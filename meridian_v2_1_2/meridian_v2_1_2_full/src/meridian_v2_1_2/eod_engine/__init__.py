"""
End-of-Day (EOD) Execution Engine for Meridian v2.1.2

Daily frequency trading with clean EOD workflow.
No intraday streaming, no tick processing, no real-time complexity.
"""

from .eod_scheduler import EODScheduler, should_run_today
from .eod_data_fetcher import fetch_eod_data, get_latest_close
from .eod_signal_runner import run_eod_signals, get_latest_signals
from .eod_order_builder import build_eod_orders, validate_orders, EODOrder
from .eod_execution_cycle import execute_eod_cycle
from .eod_logs import EODLogger, log_eod_results

__all__ = [
    'EODScheduler',
    'should_run_today',
    'fetch_eod_data',
    'get_latest_close',
    'run_eod_signals',
    'get_latest_signals',
    'build_eod_orders',
    'validate_orders',
    'EODOrder',
    'execute_eod_cycle',
    'EODLogger',
    'log_eod_results',
]

