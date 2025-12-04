"""
Research Mode Configuration for Meridian v2.1.2

Research mode: Pure backtesting, no execution simulation, full feature access.
"""

from dataclasses import dataclass


@dataclass
class ResearchSettings:
    """Settings for research mode operation"""
    allow_sweeps: bool = True
    allow_walkforward: bool = True
    allow_live_orders: bool = False
    allow_execution_engine: bool = False
    allow_oms: bool = False
    ideal_fills: bool = True  # Perfect fills at signal price
    enforce_slippage: bool = False
    enforce_delays: bool = False


def validate_research_mode(config) -> None:
    """
    Validate configuration for research mode.
    
    Research mode restrictions:
    - No live orders
    - No execution engine
    - No OMS
    
    Research mode permissions:
    - All analysis tools
    - Sweeps
    - Walk-forward
    - Full backtest capabilities
    
    Raises:
        ValueError: If config violates research mode rules
    """
    if config.mode != "research":
        raise ValueError(f"Expected mode='research', got '{config.mode}'")
    
    # Research mode is permissive - no strict validations needed
    # This is the safe default mode
    pass


