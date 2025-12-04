"""
Operator Dashboard UI for Meridian v2.1.2

Local web-based control center and monitoring system.
"""

from .dashboard_config import DashboardConfig
from .server import start_dashboard
from .data_api import DashboardAPI

__all__ = [
    'DashboardConfig',
    'start_dashboard',
    'DashboardAPI',
]


