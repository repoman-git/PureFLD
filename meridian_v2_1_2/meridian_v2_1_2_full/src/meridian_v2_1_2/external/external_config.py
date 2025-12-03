"""
External Integration Configuration for Meridian v2.1.2

Controls when and how external APIs are used.
"""

from dataclasses import dataclass


@dataclass
class ExternalConfig:
    """
    Configuration for external API integration.
    
    SAFETY PRINCIPLE: All real APIs are OFF by default.
    """
    
    # API enablement (OFF by default)
    use_openbb: bool = False
    use_alpaca: bool = False
    
    # Trading safety (LOCKED by default)
    live_trading: bool = False
    paper_trading: bool = True
    validate_keys_on_startup: bool = True
    
    # Timeouts & retry rules
    timeout_seconds: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    
    # Local fallback (ENABLED by default)
    fallback_to_synthetic_if_failed: bool = True
    fallback_to_cached: bool = True
    
    # Rate limits
    openbb_rate_limit: int = 5  # per second
    alpaca_rate_limit: int = 200  # per minute
    
    # Order safety
    max_order_size: float = 1000.0
    max_position_size: float = 10000.0
    require_model_risk_check: bool = False
    
    # Logging
    log_all_api_calls: bool = True
    log_order_attempts: bool = True

