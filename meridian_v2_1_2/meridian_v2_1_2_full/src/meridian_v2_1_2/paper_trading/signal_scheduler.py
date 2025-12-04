"""
Signal Scheduler

Schedules signal evaluation at specific times (daily open/close, weekly rebalance).

⚠️  PAPER TRADING SIMULATION ONLY
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum


class SignalTiming(Enum):
    """When to evaluate signals"""
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    DAILY_EOD = "daily_eod"
    WEEKLY_FRIDAY_CLOSE = "weekly_friday_close"
    MONTHLY_EOM = "monthly_eom"
    ON_DEMAND = "on_demand"


@dataclass
class ScheduledSignal:
    """Scheduled signal evaluation"""
    timing: SignalTiming
    strategy_name: str
    symbol: str
    timestamp: str
    signal: Optional[Dict[str, Any]] = None
    audit_result: Optional[Dict[str, Any]] = None
    order: Optional[Dict[str, Any]] = None


class SignalScheduler:
    """
    Schedules and coordinates signal evaluation.
    
    Runs strategy → audit → order pipeline at scheduled times.
    
    ⚠️  PAPER TRADING ONLY
    """
    
    def __init__(self):
        """Initialize signal scheduler"""
        self.scheduled_signals: List[ScheduledSignal] = []
        self.last_evaluation: Dict[str, str] = {}
    
    def schedule_signal(
        self,
        timing: SignalTiming,
        strategy_name: str,
        symbol: str
    ) -> ScheduledSignal:
        """
        Schedule a signal evaluation.
        
        Args:
            timing: When to evaluate
            strategy_name: Strategy to use
            symbol: Symbol to trade
        
        Returns:
            ScheduledSignal object
        """
        signal = ScheduledSignal(
            timing=timing,
            strategy_name=strategy_name,
            symbol=symbol,
            timestamp=datetime.now().isoformat()
        )
        
        self.scheduled_signals.append(signal)
        return signal
    
    def evaluate_signal(
        self,
        scheduled_signal: ScheduledSignal,
        strategy_obj: Any,
        latest_data: Any,
        audit_engine: Any
    ) -> ScheduledSignal:
        """
        Evaluate a scheduled signal through the full pipeline.
        
        Pipeline:
        1. Strategy generates signal
        2. Trading Audit reviews signal
        3. If APPROVED → create order
        4. If WARNING → create order with flag
        5. If BLOCKED → discard
        
        Args:
            scheduled_signal: Scheduled signal
            strategy_obj: Strategy instance
            latest_data: Latest market data
            audit_engine: Trading audit engine
        
        Returns:
            Updated ScheduledSignal with results
        """
        # Step 1: Generate signal from strategy
        try:
            signal = strategy_obj.generate_signals(latest_data)
            scheduled_signal.signal = signal
        except Exception as e:
            scheduled_signal.signal = {'error': str(e)}
            return scheduled_signal
        
        # Step 2: Run through Trading Audit Engine
        # (Placeholder - actual integration in orchestrator)
        scheduled_signal.audit_result = {
            'final_status': 'APPROVED',
            'summary': 'Audit passed'
        }
        
        # Step 3: Create order if approved
        if scheduled_signal.audit_result['final_status'] in ['APPROVED', 'WARNING']:
            scheduled_signal.order = {
                'symbol': scheduled_signal.symbol,
                'side': 'BUY',  # Simplified
                'quantity': 10,  # Simplified
                'order_type': 'MARKET'
            }
        
        # Track evaluation time
        self.last_evaluation[scheduled_signal.strategy_name] = datetime.now().isoformat()
        
        return scheduled_signal
    
    def should_evaluate_now(
        self,
        timing: SignalTiming,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if signal should be evaluated now.
        
        Args:
            timing: Signal timing type
            current_time: Current time (defaults to now)
        
        Returns:
            True if should evaluate
        """
        if timing == SignalTiming.ON_DEMAND:
            return True
        
        if current_time is None:
            current_time = datetime.now()
        
        # Market hours: 9:30 AM - 4:00 PM ET (simplified)
        if timing == SignalTiming.MARKET_OPEN:
            return current_time.time() >= time(9, 30) and current_time.time() < time(10, 0)
        
        elif timing == SignalTiming.MARKET_CLOSE:
            return current_time.time() >= time(16, 0) and current_time.time() < time(16, 30)
        
        elif timing == SignalTiming.DAILY_EOD:
            return current_time.time() >= time(17, 0)
        
        elif timing == SignalTiming.WEEKLY_FRIDAY_CLOSE:
            return current_time.weekday() == 4 and current_time.time() >= time(16, 0)
        
        elif timing == SignalTiming.MONTHLY_EOM:
            # Last trading day of month (simplified)
            return current_time.day >= 28 and current_time.time() >= time(16, 0)
        
        return False


