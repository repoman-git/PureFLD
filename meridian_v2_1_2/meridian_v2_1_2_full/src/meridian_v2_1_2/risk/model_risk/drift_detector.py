"""
Drift Detector for Meridian v2.1.2

Detects parameter drift, weight drift, and regime instability.
"""

import numpy as np
from typing import Dict, List


def compute_weight_drift(
    weights_history: List[Dict[str, float]],
    window: int = 10
) -> float:
    """
    Compute drift in strategy weights.
    
    Args:
        weights_history: Historical weights
        window: Lookback window
    
    Returns:
        Drift magnitude
    """
    if len(weights_history) < window:
        return 0.0
    
    recent_weights = weights_history[-window:]
    
    # Get all strategies
    all_strategies = set()
    for weights in recent_weights:
        all_strategies.update(weights.keys())
    
    # Compute drift for each strategy
    total_drift = 0.0
    
    for strategy in all_strategies:
        weight_series = [w.get(strategy, 0.0) for w in recent_weights]
        
        # Drift = mean absolute change
        if len(weight_series) > 1:
            changes = np.abs(np.diff(weight_series))
            drift = np.mean(changes)
            total_drift += drift
    
    return total_drift / len(all_strategies) if all_strategies else 0.0


def detect_drift(
    weights_history: List[Dict[str, float]] = None,
    regime_history: List[str] = None,
    max_drift: float = 0.15
) -> Dict[str, any]:
    """
    Detect parameter and regime drift.
    
    Args:
        weights_history: Historical strategy weights
        regime_history: Historical regime labels
        max_drift: Maximum acceptable drift
    
    Returns:
        Drift detection results
    """
    results = {
        'drift_detected': False,
        'weight_drift': 0.0,
        'regime_instability': 0.0,
        'is_safe': True,
        'message': 'No drift detected'
    }
    
    # Weight drift
    if weights_history and len(weights_history) > 1:
        weight_drift = compute_weight_drift(weights_history)
        results['weight_drift'] = weight_drift
        
        if weight_drift > max_drift:
            results['drift_detected'] = True
            results['is_safe'] = False
            results['message'] = f"Weight drift detected: {weight_drift:.3f}"
    
    # Regime instability
    if regime_history and len(regime_history) > 1:
        regime_instability = _compute_regime_instability(regime_history)
        results['regime_instability'] = regime_instability
        
        if regime_instability > 0.5:  # More than 50% switches
            results['drift_detected'] = True
            results['is_safe'] = False
            results['message'] = "High regime instability detected"
    
    return results


def _compute_regime_instability(regime_history: List[str]) -> float:
    """
    Compute regime switching frequency.
    
    Args:
        regime_history: List of regime labels
    
    Returns:
        Instability score (0-1)
    """
    if len(regime_history) < 2:
        return 0.0
    
    # Count regime switches
    switches = sum(1 for i in range(1, len(regime_history)) 
                   if regime_history[i] != regime_history[i-1])
    
    # Normalize by max possible switches
    max_switches = len(regime_history) - 1
    
    return switches / max_switches if max_switches > 0 else 0.0


def detect_meta_learning_runaway(
    weights_history: List[Dict[str, float]],
    threshold: float = 0.3
) -> bool:
    """
    Detect if meta-learning weights are running away.
    
    Args:
        weights_history: Historical weights
        threshold: Runaway threshold
    
    Returns:
        True if runaway detected
    """
    if len(weights_history) < 5:
        return False
    
    recent = weights_history[-5:]
    
    # Check if any weight is accelerating
    for strategy in recent[0].keys():
        weights = [w.get(strategy, 0.0) for w in recent]
        
        # Compute acceleration
        if len(weights) >= 3:
            accel = abs(weights[-1] - 2*weights[-2] + weights[-3])
            if accel > threshold:
                return True
    
    return False

