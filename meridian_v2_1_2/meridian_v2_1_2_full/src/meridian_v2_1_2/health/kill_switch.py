"""
Kill Switch for Meridian v2.1.2

Emergency stop mechanism for production safety.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime


class KillSwitch:
    """
    Emergency kill switch for trading system.
    
    Triggers on:
    - Excessive drawdown
    - Connection failures
    - Persistent drift
    - Data integrity failures
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.triggered = False
        self.trigger_time = None
        self.trigger_reason = None
    
    def trigger(self, reason: str) -> None:
        """
        Trigger kill switch.
        
        Args:
            reason: Reason for triggering
        """
        if not self.enabled:
            print(f"[KILL SWITCH] Would trigger (disabled): {reason}")
            return
        
        self.triggered = True
        self.trigger_time = datetime.now()
        self.trigger_reason = reason
        
        print(f"[KILL SWITCH] TRIGGERED: {reason}")
        print(f"[KILL SWITCH] Time: {self.trigger_time}")
        print(f"[KILL SWITCH] Action: FLATTEN ALL POSITIONS")
    
    def reset(self) -> None:
        """Reset kill switch after manual intervention"""
        self.triggered = False
        self.trigger_time = None
        self.trigger_reason = None
    
    def is_triggered(self) -> bool:
        """Check if kill switch is active"""
        return self.triggered


def should_trigger_kill_switch(
    equity_curve: Optional[Dict],
    health_status: Optional[Dict],
    drawdown_threshold: float = 0.10
) -> Tuple[bool, str]:
    """
    Determine if kill switch should trigger.
    
    Args:
        equity_curve: Equity history
        health_status: Recent health check results
        drawdown_threshold: Maximum allowed drawdown
    
    Returns:
        Tuple[bool, str]: (should_trigger, reason)
    """
    # Check drawdown
    if equity_curve and 'drawdown' in equity_curve:
        current_dd = equity_curve['drawdown']
        if current_dd < -drawdown_threshold:
            return True, f"Drawdown {current_dd:.1%} exceeds threshold {drawdown_threshold:.1%}"
    
    # Check health failures
    if health_status and health_status.get('status') == 'FAIL':
        return True, f"Health check failed: {health_status.get('details')}"
    
    return False, "No trigger conditions met"

