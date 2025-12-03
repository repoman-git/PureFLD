"""
EOD State Machine for Meridian v2.1.2

Clean state-based execution flow for daily trading loop.
"""

from enum import Enum, auto


class EODState(str, Enum):
    """States in the EOD trading loop"""
    INIT = "init"
    LOAD_DATA = "load_data"
    GENERATE_SIGNALS = "generate_signals"
    RUN_MODEL_RISK = "run_model_risk"
    EXECUTE_ORDERS = "execute_orders"
    UPDATE_PORTFOLIO = "update_portfolio"
    CALCULATE_PNL = "calculate_pnl"
    WRITE_LOGS = "write_logs"
    SAFE_MODE = "safe_mode"
    END = "end"


class EODStateMachine:
    """
    State machine for EOD trading loop.
    
    Ensures clean transitions and error handling.
    """
    
    def __init__(self, initial_state: EODState = EODState.INIT):
        """
        Initialize state machine.
        
        Args:
            initial_state: Starting state
        """
        self.current_state = initial_state
        self.state_history = [initial_state]
        self.errors = []
    
    def transition(self, new_state: EODState, error: str = None):
        """
        Transition to new state.
        
        Args:
            new_state: Target state
            error: Error message if applicable
        """
        self.current_state = new_state
        self.state_history.append(new_state)
        
        if error:
            self.errors.append({
                'state': new_state,
                'error': error
            })
    
    def is_safe(self) -> bool:
        """Check if system is not in SAFE_MODE"""
        return self.current_state != EODState.SAFE_MODE
    
    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return len(self.errors) > 0
    
    def get_state_sequence(self) -> list:
        """Get full state transition sequence"""
        return [s.value for s in self.state_history]

