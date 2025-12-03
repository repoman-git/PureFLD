"""
Oversight Configuration for Meridian v2.1.2

Controls AI monitoring system behavior.
"""

from dataclasses import dataclass


@dataclass
class OversightConfig:
    """
    Configuration for Strategy Oversight AI.
    
    Controls intelligent monitoring and supervision.
    """
    
    # Master switch
    enabled: bool = True
    
    # Monitoring frequency
    run_every_minutes: int = 5
    
    # AI reasoning modes
    enable_ai_reasoner: bool = True
    enable_behavior_learning: bool = True
    
    # Anomaly detection thresholds
    anomaly_alert_threshold: float = 0.7  # 0-1 scale
    risk_alert_threshold: float = 0.6
    
    # Behavioral learning
    baseline_lookback_days: int = 30
    deviation_threshold: float = 2.0  # Std devs
    
    # Outputs
    write_reports: bool = True
    notify_operator: bool = True
    report_path: str = "logs/oversight/"
    
    # Integration
    integrate_with_live_mode: bool = True
    integrate_with_shadow: bool = True
    integrate_with_model_risk: bool = True

