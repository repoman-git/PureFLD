"""
Broker Position Shadowing Engine for Meridian v2.1.2

Ensures local state matches broker state (paper or live).
"""

from .shadow_config import ShadowConfig
from .shadow_events import ShadowEvent, ShadowEventType
from .shadow_compare import ShadowCompare, DriftLevel, DriftResult
from .shadow_repair import ShadowRepair, RepairAction
from .shadow_engine import ShadowEngine
from .shadow_reporter import generate_shadow_report

__all__ = [
    'ShadowConfig',
    'ShadowEvent',
    'ShadowEventType',
    'ShadowCompare',
    'DriftLevel',
    'DriftResult',
    'ShadowRepair',
    'RepairAction',
    'ShadowEngine',
    'generate_shadow_report',
]


