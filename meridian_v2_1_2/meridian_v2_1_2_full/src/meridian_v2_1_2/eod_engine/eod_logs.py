"""
EOD Logging for Meridian v2.1.2

Log end-of-day execution results, performance, and OMS state.
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class EODLogger:
    """
    End-of-day logging system.
    
    Writes:
    - Performance logs
    - Order logs
    - Position logs
    - Reconciliation logs
    """
    
    def __init__(self, log_dir: str = "logs/eod"):
        """
        Initialize EOD logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_cycle(self, cycle_results: Dict) -> None:
        """
        Log complete EOD cycle results.
        
        Args:
            cycle_results: Results from execute_eod_cycle()
        """
        timestamp = cycle_results.get('timestamp', datetime.now())
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Write summary
        summary_file = self.log_dir / f"eod_summary_{date_str}.json"
        
        summary = {
            'date': date_str,
            'timestamp': str(timestamp),
            'num_symbols': len(cycle_results.get('symbols', [])),
            'num_orders': cycle_results.get('num_orders', 0),
            'signals': cycle_results.get('signals', {}),
            'target_positions': cycle_results.get('target_positions', {})
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)


def log_eod_results(
    results: Dict[str, Any],
    log_dir: str = "logs/eod"
) -> None:
    """
    Simple function to log EOD results.
    
    Args:
        results: EOD cycle results
        log_dir: Log directory
    """
    logger = EODLogger(log_dir)
    logger.log_cycle(results)


