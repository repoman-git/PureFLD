"""
Shadow Configuration for Meridian v2.1.2

Controls broker position shadowing behavior.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class ShadowConfig:
    """
    Broker position shadowing configuration.
    
    SAFETY PRINCIPLE: Paper mode by default, live optional.
    """
    
    # Master switch
    enabled: bool = True
    
    # Paper or live broker account
    mode: Literal["paper", "live"] = "paper"
    
    # Polling interval (seconds)
    interval_seconds: int = 60
    
    # Drift thresholds
    max_quantity_drift: float = 0.01  # 1% quantity drift allowed
    max_notional_drift: float = 100.0  # $100 notional drift allowed
    max_pnl_drift_pct: float = 0.5  # 0.5% PnL drift allowed
    
    # Repair behavior
    auto_repair: bool = True
    require_confirmation: bool = False
    
    # Reporting
    write_shadow_reports: bool = True
    report_path: str = "logs/shadow/"

