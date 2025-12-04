"""
Stress Testing & Chaos Engineering for Meridian v2.1.2

Chaos Monkey for quantitative trading systems.
"""

from .chaos_injector import (
    inject_price_gaps,
    inject_missing_bars,
    inject_nan_bursts,
    inject_cycle_breaks,
    inject_regime_corruption,
    inject_correlation_breaks,
    inject_oms_corruption
)

from .market_shocks import (
    volatility_explosion,
    flash_crash,
    rate_shock,
    macro_whiplash,
    liquidity_freeze,
    cot_data_freeze,
    regime_whiplash,
    cycle_inversion
)

from .failure_modes import (
    duplicate_orders,
    multiple_fills,
    extreme_slippage,
    drift_explosion,
    nav_failure,
    attribution_breakdown
)

from .stress_runner import run_stress_tests, StressTestResult
from .stress_reporter import generate_stress_report

__all__ = [
    'inject_price_gaps',
    'inject_missing_bars',
    'inject_nan_bursts',
    'inject_cycle_breaks',
    'inject_regime_corruption',
    'inject_correlation_breaks',
    'inject_oms_corruption',
    'volatility_explosion',
    'flash_crash',
    'rate_shock',
    'macro_whiplash',
    'liquidity_freeze',
    'cot_data_freeze',
    'regime_whiplash',
    'cycle_inversion',
    'duplicate_orders',
    'multiple_fills',
    'extreme_slippage',
    'drift_explosion',
    'nav_failure',
    'attribution_breakdown',
    'run_stress_tests',
    'StressTestResult',
    'generate_stress_report',
]


