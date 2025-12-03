"""
Portfolio Heatmap Component

Grid visualization of drift, exposure, and conflicts.
"""

from typing import Dict, List, Any
import numpy as np


class PortfolioHeatmap:
    """
    Portfolio heatmap component.
    
    Returns grid representing:
    - Drift severity
    - Exposure concentration
    - Conflict density
    - Anomaly flags
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get heatmap grid data.
        
        Returns:
            Dictionary with heatmap grids
        """
        portfolio = self.api.get_portfolio_overview()
        
        strategies = portfolio['strategies']
        
        if not strategies:
            return {
                'drift_grid': [],
                'exposure_grid': [],
                'conflict_grid': [],
                'labels': []
            }
        
        # Build grids
        drift_values = []
        exposure_values = []
        conflict_values = []
        labels = []
        
        for strat in strategies:
            labels.append(strat['name'])
            
            # Drift severity (0-1 scale)
            health_status = strat.get('health_status', 'ok')
            drift = {
                'ok': 0.0,
                'healthy': 0.0,
                'warning': 0.5,
                'error': 1.0,
                'unknown': 0.3
            }.get(health_status.lower(), 0.3)
            
            drift_values.append(drift)
            
            # Exposure concentration
            exposure_norm = abs(strat.get('exposure', 0.0)) / 100000  # Normalize
            exposure_values.append(min(exposure_norm, 1.0))
            
            # Conflict (based on risk score)
            risk = strat.get('risk_score', 0.0)
            conflict = min(risk / 10.0, 1.0)  # Normalize to 0-1
            conflict_values.append(conflict)
        
        # Convert to 2D grids (1xN for single row)
        return {
            'drift_grid': [drift_values],
            'exposure_grid': [exposure_values],
            'conflict_grid': [conflict_values],
            'anomaly_grid': [self._detect_anomalies(strategies)],
            'labels': labels,
            'timestamp': portfolio['timestamp']
        }
    
    def _detect_anomalies(self, strategies: List[Dict[str, Any]]) -> List[float]:
        """Detect anomalous strategy states"""
        anomalies = []
        
        for strat in strategies:
            # Simple anomaly detection
            anomaly_score = 0.0
            
            # High risk + negative PnL = anomaly
            if strat['risk_score'] > 5.0 and strat['pnl'] < 0:
                anomaly_score = 1.0
            
            # Large exposure + error health = anomaly
            if abs(strat['exposure']) > 50000 and strat.get('health_status') == 'error':
                anomaly_score = max(anomaly_score, 0.8)
            
            anomalies.append(anomaly_score)
        
        return anomalies

