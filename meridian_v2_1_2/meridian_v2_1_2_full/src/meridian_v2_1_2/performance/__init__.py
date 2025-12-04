"""
Performance Attribution Engine for Meridian v2.1.2

Break down PnL by strategy, asset, regime, cycle, risk, and execution quality.
"""

from .pnl_decomposer import decompose_pnl, compute_daily_pnl
from .strategy_attribution import attribute_to_strategies
from .asset_attribution import attribute_to_assets
from .regime_attribution import attribute_to_regimes
from .cycle_attribution import attribute_to_cycles
from .risk_attribution import attribute_to_risk_factors
from .perf_reporter import PerformanceReporter, generate_attribution_report

__all__ = [
    'decompose_pnl',
    'compute_daily_pnl',
    'attribute_to_strategies',
    'attribute_to_assets',
    'attribute_to_regimes',
    'attribute_to_cycles',
    'attribute_to_risk_factors',
    'PerformanceReporter',
    'generate_attribution_report',
]


