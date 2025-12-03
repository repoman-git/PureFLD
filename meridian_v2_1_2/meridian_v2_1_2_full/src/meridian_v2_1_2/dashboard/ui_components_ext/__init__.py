"""
Dashboard UI Extensions for Meridian v2.1.2

Advanced visualization and diagnostic components.
"""

from .pnl_multi_view import render_pnl_multi_view
from .trade_drilldown_view import render_trade_drilldown
from .risk_matrix import render_risk_matrix
from .shadow_heatmap import render_shadow_heatmap
from .oversight_timeline import render_oversight_timeline
from .notifications_panel import render_notifications
from .activity_feed import render_activity_feed
from .regime_context_view import render_regime_context

__all__ = [
    'render_pnl_multi_view',
    'render_trade_drilldown',
    'render_risk_matrix',
    'render_shadow_heatmap',
    'render_oversight_timeline',
    'render_notifications',
    'render_activity_feed',
    'render_regime_context',
]

