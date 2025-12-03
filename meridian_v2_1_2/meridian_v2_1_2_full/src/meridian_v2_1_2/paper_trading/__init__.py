"""
Paper Trading Module for Meridian v2.1.2

Real-time simulated trading environment.
Live data, simulated execution, zero real-money risk.

⚠️  EDUCATIONAL ONLY - NOT REAL TRADING
"""

from .data_feed import LiveDataFeed, fetch_latest_price
from .portfolio_state import PortfolioState, Position
from .fill_simulator import FillSimulator, SimulatedFill
from .pnl_engine import PnLEngine, PnLReport
from .signal_scheduler import SignalScheduler, ScheduledSignal
from .trade_history import TradeHistory, TradeRecord
from .paper_trading_orchestrator import PaperTradingOrchestrator

__all__ = [
    'LiveDataFeed',
    'fetch_latest_price',
    'PortfolioState',
    'Position',
    'FillSimulator',
    'SimulatedFill',
    'PnLEngine',
    'PnLReport',
    'SignalScheduler',
    'ScheduledSignal',
    'TradeHistory',
    'TradeRecord',
    'PaperTradingOrchestrator',
]

