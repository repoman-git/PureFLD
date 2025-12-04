"""
Shadow Repair for Meridian v2.1.2

Repairs drift between local and broker state.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

from .shadow_compare import DriftResult, DriftLevel
from .shadow_events import ShadowEvent, ShadowEventType


@dataclass
class RepairAction:
    """Repair action record"""
    action_type: str
    symbol: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime


class ShadowRepair:
    """
    Repairs drift between local and broker state.
    
    Actions:
    - Update local position quantities
    - Adjust cost basis
    - Add missing fills
    - Mark completed orders
    - Sync cash/equity
    """
    
    def __init__(self, config, state_store=None):
        """
        Initialize shadow repair.
        
        Args:
            config: ShadowConfig instance
            state_store: StateStore for persistence
        """
        self.config = config
        self.state_store = state_store
        self.repair_history = []
    
    def repair(
        self,
        drift_result: DriftResult,
        local_positions: Dict[str, Dict[str, float]],
        broker_positions: Dict[str, Dict[str, float]]
    ) -> List[RepairAction]:
        """
        Apply repairs based on drift result.
        
        Args:
            drift_result: Drift analysis result
            local_positions: Current local positions
            broker_positions: Broker positions (source of truth)
        
        Returns:
            List of repair actions applied
        """
        actions = []
        
        # Check if repair is allowed
        if not self._should_repair(drift_result):
            return actions
        
        # Repair position mismatches
        for mismatch in drift_result.positions_diff.get('mismatches', []):
            action = self._repair_position_mismatch(mismatch, broker_positions)
            if action:
                actions.append(action)
        
        # Repair missing local positions
        for missing in drift_result.positions_diff.get('missing_local', []):
            action = self._repair_missing_local(missing, broker_positions)
            if action:
                actions.append(action)
        
        # Repair missing broker positions (should rarely happen)
        for missing in drift_result.positions_diff.get('missing_broker', []):
            action = self._repair_missing_broker(missing)
            if action:
                actions.append(action)
        
        # Store actions
        self.repair_history.extend(actions)
        
        return actions
    
    def _should_repair(self, drift_result: DriftResult) -> bool:
        """Check if repair should be applied"""
        # Don't repair if no drift
        if drift_result.drift_level == DriftLevel.NONE:
            return False
        
        # Don't repair if critical without confirmation
        if drift_result.drift_level == DriftLevel.CRITICAL:
            if self.config.require_confirmation:
                return False
        
        # Don't repair if auto_repair disabled
        if not self.config.auto_repair:
            return False
        
        return True
    
    def _repair_position_mismatch(
        self,
        mismatch: Dict[str, Any],
        broker_positions: Dict[str, Dict[str, float]]
    ) -> Optional[RepairAction]:
        """Repair position quantity mismatch"""
        symbol = mismatch['symbol']
        broker_qty = mismatch['broker_qty']
        
        # Update local state to match broker
        # (In real implementation, would update state_store)
        
        return RepairAction(
            action_type='position_update',
            symbol=symbol,
            details={
                'old_qty': mismatch['local_qty'],
                'new_qty': broker_qty,
                'reason': 'quantity_mismatch'
            },
            timestamp=datetime.now()
        )
    
    def _repair_missing_local(
        self,
        missing: Dict[str, Any],
        broker_positions: Dict[str, Dict[str, float]]
    ) -> Optional[RepairAction]:
        """Add missing position to local state"""
        symbol = missing['symbol']
        broker_qty = missing['broker_qty']
        
        # Add position to local state
        # (In real implementation, would update state_store)
        
        return RepairAction(
            action_type='position_add',
            symbol=symbol,
            details={
                'qty': broker_qty,
                'reason': 'missing_from_local'
            },
            timestamp=datetime.now()
        )
    
    def _repair_missing_broker(
        self,
        missing: Dict[str, Any]
    ) -> Optional[RepairAction]:
        """Remove position that doesn't exist in broker"""
        symbol = missing['symbol']
        local_qty = missing['local_qty']
        
        # Remove from local state
        # (In real implementation, would update state_store)
        
        return RepairAction(
            action_type='position_remove',
            symbol=symbol,
            details={
                'qty': local_qty,
                'reason': 'not_in_broker'
            },
            timestamp=datetime.now()
        )
    
    def get_repair_summary(self) -> Dict[str, Any]:
        """Get summary of repair actions"""
        return {
            'total_actions': len(self.repair_history),
            'by_type': self._count_by_type(),
            'last_repair': self.repair_history[-1] if self.repair_history else None
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count repairs by type"""
        counts = {}
        for action in self.repair_history:
            action_type = action.action_type
            counts[action_type] = counts.get(action_type, 0) + 1
        return counts


