"""
Hurst Cycle Analysis Module

Professional cycle analysis based on J.M. Hurst's principles:
- Phase computation using Hilbert transform
- Trough detection across multiple cycle periods
- Valid Trend Line (VTL) construction
- VTL break detection for trade signals
- Cycle diagnostics and validation

⚠️  EDUCATIONAL ONLY - Not investment advice
"""

from .hurst_phasing import HurstPhasingEngine
from .hurst_vtl import HurstVTLBuilder, HurstVTLBreakDetector
from .hurst_diagnostics import HurstDiagnostics
from .hurst_plotting import plot_hurst_view, plot_phase_vs_price
from .hurst_visual_full import plot_sentient_trader_full, plot_sentient_trader_interactive
from .hurst_right_translation import RightTranslationAdjuster
from .hurst_dashboard_plotly import plot_sentient_dashboard, create_multi_cycle_comparison

__all__ = [
    'HurstPhasingEngine',
    'HurstVTLBuilder',
    'HurstVTLBreakDetector',
    'HurstDiagnostics',
    'plot_hurst_view',
    'plot_phase_vs_price',
    'plot_sentient_trader_full',
    'plot_sentient_trader_interactive',
    'RightTranslationAdjuster',
    'plot_sentient_dashboard',
    'create_multi_cycle_comparison',
]

