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

__all__ = [
    'HurstPhasingEngine',
    'HurstVTLBuilder',
    'HurstVTLBreakDetector',
    'HurstDiagnostics',
    'plot_hurst_view',
    'plot_phase_vs_price',
]

