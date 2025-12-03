"""
Regime Dependency Analyzer for Meridian v2.1.2

Measures strategy dependence on specific market regimes.
"""

import numpy as np
from typing import Dict, List, Any


def compute_dependency_score(
    regime_pnl: Dict[str, float]
) -> float:
    """
    Compute regime dependency score.
    
    dependency = max_regime_pnl / total_pnl
    
    Args:
        regime_pnl: PnL by regime
    
    Returns:
        Dependency score (0-1)
    """
    if not regime_pnl:
        return 0.0
    
    total_pnl = sum(regime_pnl.values())
    
    if total_pnl == 0:
        return 0.0
    
    max_regime_pnl = max(regime_pnl.values())
    
    return max_regime_pnl / total_pnl


def analyze_regime_dependency(
    pnl_by_regime: Dict[str, float],
    max_dependency: float = 0.5
) -> Dict[str, Any]:
    """
    Analyze strategy dependence on regimes.
    
    Args:
        pnl_by_regime: PnL breakdown by regime
        max_dependency: Maximum acceptable dependency
    
    Returns:
        Dependency analysis results
    """
    if not pnl_by_regime:
        return {
            'is_diversified': True,
            'dependency_score': 0.0,
            'dominant_regime': None,
            'message': 'No regime data available'
        }
    
    dependency_score = compute_dependency_score(pnl_by_regime)
    
    # Find dominant regime
    dominant_regime = max(pnl_by_regime, key=pnl_by_regime.get)
    dominant_pnl = pnl_by_regime[dominant_regime]
    
    is_diversified = dependency_score <= max_dependency
    
    # Compute regime concentration
    regime_concentration = _compute_herfindahl_index(pnl_by_regime)
    
    return {
        'is_diversified': is_diversified,
        'dependency_score': dependency_score,
        'dominant_regime': dominant_regime,
        'dominant_pnl': dominant_pnl,
        'regime_concentration': regime_concentration,
        'regime_breakdown': pnl_by_regime,
        'message': f"Dependency score: {dependency_score:.2f} (threshold: {max_dependency:.2f})"
    }


def _compute_herfindahl_index(pnl_by_regime: Dict[str, float]) -> float:
    """
    Compute Herfindahl-Hirschman Index for regime concentration.
    
    HHI = sum(market_share^2)
    
    Args:
        pnl_by_regime: PnL by regime
    
    Returns:
        HHI (0-1, higher = more concentrated)
    """
    total_pnl = sum(abs(p) for p in pnl_by_regime.values())
    
    if total_pnl == 0:
        return 0.0
    
    shares = [abs(p) / total_pnl for p in pnl_by_regime.values()]
    hhi = sum(s**2 for s in shares)
    
    return hhi


def analyze_cycle_dependency(
    pnl_by_cycle_phase: Dict[str, float],
    max_dependency: float = 0.6
) -> Dict[str, Any]:
    """
    Analyze strategy dependence on cycle phases.
    
    Args:
        pnl_by_cycle_phase: PnL by cycle phase
        max_dependency: Maximum acceptable dependency
    
    Returns:
        Cycle dependency analysis
    """
    if not pnl_by_cycle_phase:
        return {
            'is_diversified': True,
            'dependency_score': 0.0,
            'dominant_phase': None
        }
    
    dependency_score = compute_dependency_score(pnl_by_cycle_phase)
    dominant_phase = max(pnl_by_cycle_phase, key=pnl_by_cycle_phase.get)
    
    return {
        'is_diversified': dependency_score <= max_dependency,
        'dependency_score': dependency_score,
        'dominant_phase': dominant_phase,
        'phase_breakdown': pnl_by_cycle_phase
    }

