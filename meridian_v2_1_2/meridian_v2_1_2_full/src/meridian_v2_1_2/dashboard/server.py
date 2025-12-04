"""
Dashboard Server for Meridian v2.1.2

Starts and manages the dashboard server.
"""

import subprocess
import sys
from pathlib import Path


def start_dashboard(config, background: bool = False):
    """
    Start the dashboard server.
    
    Args:
        config: DashboardConfig instance
        background: Run in background mode
    
    Returns:
        Process if background, None otherwise
    """
    if not config.enabled:
        print("Dashboard is disabled in config")
        return None
    
    # Get path to UI file
    ui_path = Path(__file__).parent / "ui.py"
    
    if not ui_path.exists():
        print(f"Dashboard UI file not found: {ui_path}")
        return None
    
    # Build streamlit command
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ui_path),
        "--server.port",
        str(config.port),
        "--server.address",
        config.host
    ]
    
    if not config.auto_open:
        cmd.extend(["--server.headless", "true"])
    
    print(f"Starting dashboard on http://{config.host}:{config.port}")
    
    if background:
        process = subprocess.Popen(cmd)
        return process
    else:
        subprocess.run(cmd)
        return None


