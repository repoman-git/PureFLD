"""
Portfolio Module for Meridian v2.1.2

Multi-strategy portfolio construction and fusion.
"""

from .fusion import blend_equity_curves, optimize_weights, FusionResult

__all__ = ['blend_equity_curves', 'optimize_weights', 'FusionResult']
