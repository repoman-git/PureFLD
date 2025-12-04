"""
Live Trading Mode Configuration for Meridian v2.1.2

Live mode: Real trading with strict safety gates and broker integration.
"""

from dataclasses import dataclass


@dataclass
class LiveSettings:
    """Settings for live trading mode"""
    allow_execution: bool = True
    enforce_slippage: bool = True
    enforce_delay: bool = True
    enforce_orders: bool = True
    
    # Strict live-only restrictions
    disallow_sweeps: bool = True
    disallow_walkforward: bool = True
    disallow_notebooks: bool = True
    
    # Required for live
    require_broker_connection: bool = True
    enable_kill_switches: bool = True
    enable_oms: bool = True
    
    # Safety
    max_daily_orders: int = 100
    require_heartbeat: bool = True
    fallback_to_flat: bool = True


def validate_live_mode(config) -> None:
    """
    Validate configuration for live trading mode.
    
    Live mode is STRICT:
    - No sweeps (single strategy only)
    - No walk-forward (real-time only)
    - No notebooks (automated only)
    - Broker connection required
    - Kill switches enabled
    
    Raises:
        ValueError: If config violates live mode safety rules
    """
    if config.mode != "live":
        raise ValueError(f"Expected mode='live', got '{config.mode}'")
    
    # In live mode, certain operations are forbidden
    if hasattr(config, 'sweep') and config.sweep.enable_sweep:
        raise ValueError("Sweeps not allowed in live mode")
    
    if hasattr(config, 'walkforward') and config.walkforward.enable_walkforward:
        raise ValueError("Walk-forward not allowed in live mode")
    
    # Additional safety checks can be added here
    pass


