"""Trading State Machine"""
from enum import Enum
from datetime import datetime

class TradingState(Enum):
    IDLE = "idle"
    SIGNAL_RECEIVED = "signal_received"
    PRETRADE_CHECK = "pretrade_check"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    ERROR = "error"

class TradingStateMachine:
    """State machine for trade execution flow"""
    
    def __init__(self):
        self.state = TradingState.IDLE
        self.history = []
    
    def transition(self, new_state: TradingState, message: str = ""):
        """Transition to new state"""
        self.history.append({
            'timestamp': datetime.now(),
            'from': self.state.value,
            'to': new_state.value,
            'message': message
        })
        self.state = new_state
    
    def get_state(self) -> TradingState:
        """Get current state"""
        return self.state
    
    def is_idle(self) -> bool:
        return self.state == TradingState.IDLE
    
    def can_execute(self) -> bool:
        return self.state == TradingState.PRETRADE_CHECK
