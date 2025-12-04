"""
Execution Engine - Core orchestrator for live trading

Author: Meridian Team
Date: December 4, 2025
"""

import pandas as pd
from typing import Dict, List, Optional
from .broker_base import BrokerBase, Order
from .order_manager import OrderManager
from .position_manager import PositionManager
from .risk_gate import RiskGate
from .state_machine import TradingStateMachine, TradingState


class ExecutionEngine:
    """
    Core orchestrator for trade execution.
    
    Integrates all Stages 1-6 with real broker execution.
    
    Example:
        >>> from meridian_v2_1_2.execution_engine import *
        >>> 
        >>> # Setup
        >>> broker = AlpacaClient(API_KEY, SECRET, PAPER_ENDPOINT)
        >>> broker.connect()
        >>> 
        >>> engine = ExecutionEngine(
        ...     broker=broker,
        ...     order_manager=OrderManager(),
        ...     position_manager=PositionManager(),
        ...     risk_gate=RiskGate()
        ... )
        >>> 
        >>> # Execute trading cycle
        >>> results = engine.step(
        ...     signals=signals,
        ...     prices=current_prices,
        ...     allocation=weights,
        ...     vol_df=volatility_metrics,
        ...     regime_state=regime_predictions
        ... )
    """
    
    def __init__(
        self,
        broker: BrokerBase,
        order_manager: OrderManager,
        position_manager: PositionManager,
        risk_gate: RiskGate
    ):
        """
        Initialize execution engine.
        
        Args:
            broker: Broker client (Alpaca, IBKR, etc.)
            order_manager: Order generation logic
            position_manager: Position tracking
            risk_gate: Risk validation
        """
        self.broker = broker
        self.orders = order_manager
        self.positions = position_manager
        self.risk = risk_gate
        self.state_machine = TradingStateMachine()
        self.execution_log = []
    
    def step(
        self,
        signals: Dict[str, pd.Series],
        prices: Dict[str, float],
        allocation: Dict[str, float],
        vol_df: Optional[pd.DataFrame] = None,
        regime_state: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Execute one trading cycle.
        
        Flow:
        1. Update positions from broker
        2. Generate candidate orders
        3. Apply risk gates
        4. Execute approved orders
        5. Log results
        
        Args:
            signals: Trading signals per symbol
            prices: Current prices per symbol
            allocation: Portfolio allocation weights
            vol_df: Volatility metrics (optional)
            regime_state: Regime predictions (optional)
            
        Returns:
            List of execution results
        """
        # State: IDLE → SIGNAL_RECEIVED
        self.state_machine.transition(TradingState.SIGNAL_RECEIVED, "Signals received")
        
        # Step 1: Update positions from broker
        try:
            broker_positions = self.broker.get_positions()
            self.positions.update(broker_positions)
        except Exception as e:
            self.state_machine.transition(TradingState.ERROR, f"Failed to fetch positions: {e}")
            return [{'error': str(e)}]
        
        # Get account info
        try:
            account = self.broker.get_account_info()
            account_value = account.portfolio_value
        except Exception as e:
            self.state_machine.transition(TradingState.ERROR, f"Failed to fetch account: {e}")
            return [{'error': str(e)}]
        
        # Step 2: Generate candidate orders
        candidate_orders = self.orders.generate_orders(
            signals=signals,
            prices=prices,
            allocation=allocation,
            account_value=account_value
        )
        
        if not candidate_orders:
            self.state_machine.transition(TradingState.IDLE, "No orders generated")
            return []
        
        # State: SIGNAL_RECEIVED → PRETRADE_CHECK
        self.state_machine.transition(TradingState.PRETRADE_CHECK, f"Checking {len(candidate_orders)} orders")
        
        # Step 3: Apply risk gates
        approved_orders = []
        for order in candidate_orders:
            allowed, reason = self.risk.validate_order(
                order=order,
                account_value=account_value,
                vol_df=vol_df,
                regime_state=regime_state,
                current_positions=self.positions.positions
            )
            
            if allowed:
                approved_orders.append(order)
            else:
                self.execution_log.append({
                    'timestamp': pd.Timestamp.now(),
                    'symbol': order.symbol,
                    'action': 'BLOCKED',
                    'reason': reason
                })
        
        # Portfolio-level risk check
        if approved_orders:
            portfolio_ok, reason = self.risk.validate_portfolio(
                approved_orders,
                self.positions.positions,
                account_value
            )
            
            if not portfolio_ok:
                self.state_machine.transition(TradingState.ERROR, reason)
                return [{'error': reason}]
        
        # State: PRETRADE_CHECK → EXECUTING
        self.state_machine.transition(TradingState.EXECUTING, f"Executing {len(approved_orders)} orders")
        
        # Step 4: Execute approved orders
        results = []
        for order in approved_orders:
            try:
                result = self.broker.submit_order(order)
                results.append(result)
                
                self.execution_log.append({
                    'timestamp': pd.Timestamp.now(),
                    'symbol': order.symbol,
                    'side': order.side,
                    'qty': order.qty,
                    'status': result.get('status', 'unknown'),
                    'order_id': result.get('order_id')
                })
            except Exception as e:
                results.append({'error': str(e), 'symbol': order.symbol})
                self.execution_log.append({
                    'timestamp': pd.Timestamp.now(),
                    'symbol': order.symbol,
                    'action': 'FAILED',
                    'error': str(e)
                })
        
        # State: EXECUTING → MONITORING
        self.state_machine.transition(TradingState.MONITORING, f"Monitoring {len(results)} orders")
        
        return results
    
    def get_execution_log(self) -> pd.DataFrame:
        """Get execution history"""
        if not self.execution_log:
            return pd.DataFrame()
        return pd.DataFrame(self.execution_log)
    
    def emergency_stop(self):
        """Cancel all orders and flatten positions"""
        try:
            self.broker.cancel_all_orders()
            # Note: Flattening positions would require generating closing orders
            self.state_machine.transition(TradingState.IDLE, "Emergency stop executed")
            return True
        except Exception as e:
            self.state_machine.transition(TradingState.ERROR, f"Emergency stop failed: {e}")
            return False
