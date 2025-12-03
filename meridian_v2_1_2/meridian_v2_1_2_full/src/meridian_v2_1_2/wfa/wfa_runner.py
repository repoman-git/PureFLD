"""
WFA Runner for Meridian v2.1.2

Orchestrates walk-forward analysis across all windows.
"""

import pandas as pd
from typing import List, Dict, Any
from .wfa_splitter import split_walkforward_windows
from .wfa_executor import execute_wfa_window


def run_walkforward_analysis(
    prices: pd.Series,
    cfg: Any
) -> List[Dict[str, Any]]:
    """
    Run complete walk-forward analysis.
    
    For each window:
    1. Fit on training data
    2. Test on OOS data
    3. Capture metrics
    4. Store results
    
    Args:
        prices: Price series
        cfg: WFA configuration
    
    Returns:
        List of window results
    """
    # Split into windows
    windows = split_walkforward_windows(
        prices.index,
        training_window=cfg.wfa.training_window,
        testing_window=cfg.wfa.testing_window,
        step_size=cfg.wfa.step_size
    )
    
    results = []
    
    for train_dates, test_dates in windows:
        # Execute window
        window_result = execute_wfa_window(
            train_dates,
            test_dates,
            prices,
            cfg
        )
        
        results.append(window_result)
    
    return results

