"""
Behavioral Patterns Tracker for Meridian v2.1.2

Learns normal system behavior and detects deviations.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np


@dataclass
class Baseline:
    """Baseline behavioral patterns"""
    avg_signal_count: float
    avg_exposure: float
    avg_turnover: float
    avg_slippage: float
    avg_fill_rate: float
    avg_drift_events: float
    sample_size: int


class BehavioralPatterns:
    """
    Tracks and learns normal system behavior.
    
    Maintains rolling baselines for:
    - Signal frequency
    - Exposure levels
    - Turnover patterns
    - Execution quality
    - Drift frequency
    """
    
    def __init__(self, config):
        """
        Initialize behavioral patterns tracker.
        
        Args:
            config: OversightConfig instance
        """
        self.config = config
        self.history = []
    
    def update(self, observation: Dict[str, Any]):
        """
        Update behavioral history.
        
        Args:
            observation: Daily metrics
        """
        self.history.append(observation)
        
        # Keep only recent history
        max_days = self.config.baseline_lookback_days
        if len(self.history) > max_days:
            self.history = self.history[-max_days:]
    
    def compute_baseline(self) -> Baseline:
        """
        Compute baseline patterns from history.
        
        Returns:
            Baseline patterns
        """
        if not self.history:
            return Baseline(
                avg_signal_count=0,
                avg_exposure=0,
                avg_turnover=0,
                avg_slippage=0,
                avg_fill_rate=1.0,
                avg_drift_events=0,
                sample_size=0
            )
        
        # Compute averages
        signal_counts = [h.get('signal_count', 0) for h in self.history]
        exposures = [h.get('total_exposure', 0) for h in self.history]
        turnovers = [h.get('daily_turnover', 0) for h in self.history]
        slippages = [h.get('avg_slippage', 0) for h in self.history]
        fill_rates = [h.get('fill_rate', 1.0) for h in self.history]
        drift_events = [h.get('drift_events', 0) for h in self.history]
        
        return Baseline(
            avg_signal_count=np.mean(signal_counts),
            avg_exposure=np.mean(exposures),
            avg_turnover=np.mean(turnovers),
            avg_slippage=np.mean(slippages),
            avg_fill_rate=np.mean(fill_rates),
            avg_drift_events=np.mean(drift_events),
            sample_size=len(self.history)
        )
    
    def detect_deviations(
        self,
        current: Dict[str, Any]
    ) -> List[str]:
        """
        Detect deviations from baseline.
        
        Args:
            current: Current metrics
        
        Returns:
            List of deviation descriptions
        """
        deviations = []
        
        if len(self.history) < 7:  # Need at least a week
            return deviations
        
        baseline = self.compute_baseline()
        threshold = self.config.deviation_threshold
        
        # Check each metric
        metrics = {
            'signal_count': (current.get('signal_count', 0), baseline.avg_signal_count),
            'total_exposure': (current.get('total_exposure', 0), baseline.avg_exposure),
            'daily_turnover': (current.get('daily_turnover', 0), baseline.avg_turnover),
        }
        
        for metric_name, (current_val, baseline_val) in metrics.items():
            if baseline_val > 0:
                # Compute historical std dev
                historical_vals = [h.get(metric_name, 0) for h in self.history]
                std_dev = np.std(historical_vals)
                
                if std_dev > 0:
                    z_score = abs(current_val - baseline_val) / std_dev
                    
                    if z_score > threshold:
                        deviations.append(
                            f"{metric_name}: {z_score:.1f} std devs from baseline"
                        )
        
        return deviations

