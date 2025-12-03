"""
Strategy Module for Meridian v2.1.2

Strategy implementations and multi-strategy fusion.
"""

# Fusion module
try:
    from .fusion import blend_equity_curves, optimize_weights, FusionResult
    __all__ = ['blend_equity_curves', 'optimize_weights', 'FusionResult']
except ImportError:
    __all__ = []

