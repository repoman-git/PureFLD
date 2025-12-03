"""
EOD Execution Cycle for Meridian v2.1.2

Orchestrates the complete end-of-day trading workflow.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from ..config import MeridianConfig
from .eod_data_fetcher import fetch_eod_data, get_latest_close
from .eod_signal_runner import run_eod_signals, get_latest_signals
from .eod_order_builder import build_eod_orders, EODOrder
from .eod_logs import EODLogger


def execute_eod_cycle(
    config: MeridianConfig,
    symbols: List[str],
    current_positions: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Execute complete end-of-day trading cycle.
    
    Daily workflow:
    1. Fetch EOD data
    2. Run signals
    3. Size positions
    4. Allocate portfolio
    5. Build orders
    6. Log results
    
    Args:
        config: Meridian configuration
        symbols: Symbols to trade
        current_positions: Current positions (from broker)
    
    Returns:
        Dict with:
            - signals: Generated signals
            - orders: Orders to execute
            - positions: Target positions
            - logs: Execution logs
    
    Notes:
        - Runs once per day
        - No intraday updates
        - Clean, predictable workflow
    """
    if current_positions is None:
        current_positions = {sym: 0.0 for sym in symbols}
    
    # Step 1: Fetch EOD data
    print(f"[{datetime.now()}] Fetching EOD data for {len(symbols)} symbols...")
    eod_data = fetch_eod_data(symbols, lookback_days=500, source="local")
    
    # Step 2: Run signals
    print(f"[{datetime.now()}] Running signal generation...")
    full_signals = run_eod_signals(eod_data, config)
    latest_signals = get_latest_signals(full_signals)
    
    # Step 3: Get latest prices
    latest_prices = get_latest_close(eod_data)
    
    # Step 4: Compute target positions
    # Simplified: signal × base_size
    # Full implementation would use risk engine + portfolio allocator
    target_positions = {}
    base_size = 1.0  # Placeholder
    
    for symbol, signal in latest_signals.items():
        target_positions[symbol] = signal * base_size
    
    # Step 5: Build orders
    print(f"[{datetime.now()}] Building orders...")
    orders = build_eod_orders(target_positions, current_positions, latest_prices)
    
    # Step 6: Log
    print(f"[{datetime.now()}] EOD cycle complete. Orders: {len(orders)}")
    
    results = {
        'timestamp': datetime.now(),
        'symbols': symbols,
        'signals': latest_signals,
        'target_positions': target_positions,
        'current_positions': current_positions,
        'orders': orders,
        'prices': latest_prices,
        'num_orders': len(orders)
    }
    
    return results

