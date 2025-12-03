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
from .hurst_fld import FLDEngine
from .hurst_fld_plotting import plot_fld
from .hurst_fld_dashboard import plot_fld_interactive
from .hurst_multitimeframe_dashboard import multi_tf_dashboard

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
    'FLDEngine',
    'plot_fld',
    'plot_fld_interactive',
    'multi_tf_dashboard',
]

