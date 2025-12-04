"""
Dashboard Configuration for Meridian v2.1.2

Controls dashboard server settings.
"""

from dataclasses import dataclass


@dataclass
class DashboardConfig:
    """
    Configuration for operator dashboard.
    
    Local web interface for monitoring and control.
    """
    
    # Master switch
    enabled: bool = True
    
    # Server settings
    host: str = "127.0.0.1"  # localhost only for security
    port: int = 8501  # Streamlit default
    
    # Behavior
    auto_open: bool = True  # Open browser automatically
    refresh_seconds: int = 10  # Auto-refresh interval
    
    # UI settings
    theme: str = "dark"  # dark | light
    show_debug_info: bool = False
    
    # Integration
    enable_approvals: bool = True
    enable_oversight_panel: bool = True
    enable_shadow_panel: bool = True
    
    # Data paths
    db_path: str = "meridian_local/meridian.db"
    logs_path: str = "logs/"


