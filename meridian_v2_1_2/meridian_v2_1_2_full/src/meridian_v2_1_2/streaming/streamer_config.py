"""
Streamer Configuration for Meridian v2.1.2

Controls data streaming behavior.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class StreamerConfig:
    """
    Configuration for data streaming layer.
    
    IMPORTANT: Streaming is for MONITORING only.
    EOD execution remains unchanged.
    """
    
    # Master switch
    enabled: bool = True
    
    # Market data (OpenBB)
    openbb_enabled: bool = True
    openbb_interval_sec: int = 15  # Poll every 15 seconds
    openbb_symbols: List[str] = None  # Defaults to ['GLD', 'LTPZ']
    
    # Broker state (Alpaca)
    alpaca_enabled: bool = True
    alpaca_interval_sec: int = 10  # Poll every 10 seconds
    alpaca_mode: str = "paper"  # paper | live
    
    # Safety features
    require_api_keys: bool = True
    timeout_sec: int = 5
    max_consecutive_failures: int = 3
    
    # Data retention
    store_streamed_bars: bool = True
    store_streamed_orders: bool = True
    max_cache_size: int = 1000
    
    # Dashboard integration
    push_to_dashboard: bool = True
    push_interval_sec: int = 10
    
    # Integration hooks
    update_shadow_engine: bool = True
    update_oversight_ai: bool = True
    
    # Reporting
    write_stream_logs: bool = True
    log_path: str = "logs/streaming/"
    
    def __post_init__(self):
        """Initialize defaults"""
        if self.openbb_symbols is None:
            self.openbb_symbols = ['GLD', 'LTPZ']

