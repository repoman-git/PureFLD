"""
Sweep Configuration for Meridian v2.1.2

Defines parameter sweep search spaces and constraints.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple
from enum import Enum


class SweepMode(str, Enum):
    """Sweep execution mode"""
    GRID = "grid"          # Full grid search
    RANDOM = "random"      # Random sampling
    CUSTOM = "custom"      # Custom parameter sets


@dataclass
class SweepConfig:
    """
    Configuration for parameter sweep.
    
    Defines the search space for hyperparameter optimization.
    """
    
    # Sweep mode
    mode: SweepMode = SweepMode.GRID
    
    # Parameter ranges - FLD
    fld_offsets: List[int] = field(default_factory=lambda: [5, 10, 15])
    fld_smoothing: List[int] = field(default_factory=lambda: [3, 5, 7])
    
    # Parameter ranges - COT
    cot_thresholds: List[float] = field(default_factory=lambda: [-0.2, 0.0, 0.2])
    cot_lookback: List[int] = field(default_factory=lambda: [50, 100, 150])
    
    # Parameter ranges - TDOM
    tdom_filter_enabled: List[bool] = field(default_factory=lambda: [True, False])
    tdom_threshold: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])
    
    # Parameter ranges - Execution
    slippage_bps: List[float] = field(default_factory=lambda: [2.0, 4.0, 8.0])
    
    # Random search settings
    random_samples: int = 50
    random_seed: int = 42
    
    # Constraints
    max_combinations: int = 1000
    
    # Parallel execution
    enable_parallel: bool = False
    n_jobs: int = 1
    
    # Metrics to optimize
    primary_metric: str = "sharpe_ratio"  # sharpe_ratio, total_return, max_drawdown, etc.
    
    # Output configuration
    save_all_results: bool = True
    save_top_n: int = 10
    output_dir: str = "outputs/sweeps/"


