"""
Shadow Events for Meridian v2.1.2

Tracks broker shadowing events.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


class ShadowEventType(str, Enum):
    """Shadow event types"""
    POSITION_DRIFT = "position_drift"
    MISSING_FILL = "missing_fill"
    GHOST_ORDER = "ghost_order"
    PNL_DIVERGENCE = "pnl_divergence"
    COST_BASIS_MISMATCH = "cost_basis_mismatch"
    REPAIR_APPLIED = "repair_applied"
    CRITICAL_DRIFT = "critical_drift"
    SHADOW_CHECK_FAILED = "shadow_check_failed"
    SHADOW_CHECK_OK = "shadow_check_ok"


@dataclass
class ShadowEvent:
    """Shadow event record"""
    event_type: ShadowEventType
    timestamp: datetime
    message: str
    severity: str  # info | warning | error | critical
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'severity': self.severity,
            'details': self.details or {}
        }


