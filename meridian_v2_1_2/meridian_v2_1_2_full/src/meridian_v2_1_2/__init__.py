"""
Meridian v2.1.2 - FLD + COT + TDOM Trading Research Framework
"""

__version__ = '2.1.2'

from .config import (
    MeridianConfig,
    FLDConfig,
    COTConfig,
    SeasonalityConfig,
    StrategyConfig,
    BacktestConfig,
    SweepConfig,
    WalkForwardConfig,
    CycleConfig
)
from .seasonality import compute_tdom_flags, compute_tdoy_flags, combine_seasonal_flags
from .strategy import FLDStrategy
try:
    from .orchestrator_legacy import run_backtest
except ImportError:
    # Use new EOD orchestrator
    from .orchestrator import run_eod_day as run_backtest
from .sweep_engine import run_parameter_sweep, write_results, get_best_parameters
from .metrics_engine import (
    compute_basic_metrics,
    compute_trade_metrics,
    compute_robustness_score,
    compute_drawdown_series,
    compute_underwater_curve
)
from .walkforward_engine import (
    generate_walkforward_splits,
    walkforward_run,
    analyze_walkforward_results
)

__all__ = [
    'MeridianConfig',
    'FLDConfig',
    'COTConfig',
    'SeasonalityConfig',
    'StrategyConfig',
    'BacktestConfig',
    'SweepConfig',
    'WalkForwardConfig',
    'compute_tdom_flags',
    'compute_tdoy_flags',
    'combine_seasonal_flags',
    'FLDStrategy',
    'run_backtest',
    'run_parameter_sweep',
    'write_results',
    'get_best_parameters',
    'compute_basic_metrics',
    'compute_trade_metrics',
    'compute_robustness_score',
    'compute_drawdown_series',
    'compute_underwater_curve',
    'generate_walkforward_splits',
    'walkforward_run',
    'analyze_walkforward_results',
]

