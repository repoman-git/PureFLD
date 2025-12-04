"""
Strategy State Machine for Meridian v2.1.2

Manages persistent strategy lifecycle states.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class StrategyState(str, Enum):
    """Strategy lifecycle states"""
    RESEARCH = "research"
    WFA_PASSED = "wfa_passed"
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    DISABLED = "disabled"


class StrategyStatus:
    """
    Represents the current status of a strategy in the incubation pipeline.
    """
    
    def __init__(
        self,
        strategy_name: str,
        state: StrategyState = StrategyState.RESEARCH,
        version: str = "v2.1.2",
        days_in_state: int = 0,
        last_transition: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.strategy_name = strategy_name
        self.state = state
        self.version = version
        self.days_in_state = days_in_state
        self.last_transition = last_transition or datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'strategy_name': self.strategy_name,
            'state': self.state.value if isinstance(self.state, StrategyState) else self.state,
            'version': self.version,
            'days_in_state': self.days_in_state,
            'last_transition': self.last_transition,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyStatus':
        """Create from dictionary"""
        return cls(
            strategy_name=data['strategy_name'],
            state=StrategyState(data['state']),
            version=data.get('version', 'v2.1.2'),
            days_in_state=data.get('days_in_state', 0),
            last_transition=data.get('last_transition'),
            metadata=data.get('metadata', {})
        )


def load_strategy_state(
    strategy_name: str,
    state_path: str = "state/strategy_status.json"
) -> StrategyStatus:
    """
    Load strategy state from persistent storage.
    
    Args:
        strategy_name: Name of strategy
        state_path: Path to state file
    
    Returns:
        StrategyStatus object
    """
    state_file = Path(state_path)
    
    if not state_file.exists():
        # Return default state
        return StrategyStatus(strategy_name=strategy_name)
    
    with open(state_file, 'r') as f:
        all_states = json.load(f)
    
    if strategy_name in all_states:
        return StrategyStatus.from_dict(all_states[strategy_name])
    else:
        return StrategyStatus(strategy_name=strategy_name)


def save_strategy_state(
    status: StrategyStatus,
    state_path: str = "state/strategy_status.json"
) -> None:
    """
    Save strategy state to persistent storage.
    
    Args:
        status: StrategyStatus to save
        state_path: Path to state file
    """
    state_file = Path(state_path)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing states
    if state_file.exists():
        with open(state_file, 'r') as f:
            all_states = json.load(f)
    else:
        all_states = {}
    
    # Update this strategy
    all_states[status.strategy_name] = status.to_dict()
    
    # Save
    with open(state_file, 'w') as f:
        json.dump(all_states, f, indent=2)


