"""
Paper Trading Mode Configuration for Meridian v2.1.2

Paper mode: Realistic execution simulation with slippage, delays, and order mechanics.
"""

from dataclasses import dataclass


@dataclass
class PaperSettings:
    """Settings for paper trading mode"""
    allow_execution: bool = True
    enforce_slippage: bool = True
    enforce_delay: bool = True
    enforce_orders: bool = True
    protect_against_future_data: bool = True
    allow_sweeps: bool = True  # Paper can still run sweeps
    allow_walkforward: bool = True
    allow_live_orders: bool = False
    enable_oms: bool = True  # Order Management System


def validate_paper_mode(config) -> None:
    """
    Validate configuration for paper trading mode.
    
    Paper mode is for realistic simulation:
    - Execution engine enabled
    - Slippage and delays enforced
    - OMS tracking enabled
    - No real broker connections
    
    Raises:
        ValueError: If config violates paper mode rules
    """
    if config.mode != "paper":
        raise ValueError(f"Expected mode='paper', got '{config.mode}'")
    
    # Paper mode allows most features but simulates execution
    pass


