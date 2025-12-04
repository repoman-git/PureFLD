"""
Execution Engine (Stage 7)

Real trading execution through multiple broker APIs.

This is the "crossing the Rubicon" moment - Meridian can now place real trades.

Features:
- Multi-broker support (Alpaca, IBKR, Tradovate)
- Paper and live trading modes
- Order management system
- Position tracking
- Risk gates and pre-trade validation
- State machine for trade flow
- Cycle-aware execution
- Integration with Stages 1-6

Brokers Supported:
- Alpaca (free paper trading, easy live)
- Interactive Brokers (institutional-grade)
- Tradovate (futures, optional)

Author: Meridian Team
Date: December 4, 2025
Stage: 7 of 10
"""

from .broker_base import BrokerBase
from .alpaca_client import AlpacaClient
from .ibkr_client import IBKRClient
from .order_manager import OrderManager
from .position_manager import PositionManager
from .risk_gate import RiskGate
from .execution_engine import ExecutionEngine
from .state_machine import TradingStateMachine

__all__ = [
    'BrokerBase',
    'AlpacaClient',
    'IBKRClient',
    'OrderManager',
    'PositionManager',
    'RiskGate',
    'ExecutionEngine',
    'TradingStateMachine',
]

__version__ = '1.0.0'
