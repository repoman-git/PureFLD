"""
Fragility Index for Meridian v2.1.2

Measures how brittle a strategy is to perturbations.
"""

import numpy as np
from typing import Dict, Any
from .sensitivity_tests import SensitivityResult


def compute_fragility_index(
    sensitivity_results: Dict[str, SensitivityResult]
) -> float:
    """
    Compute overall fragility index.
    
    fragility = mean(|PnL_change|) / perturbation_size
    
    Args:
        sensitivity_results: Results from sensitivity tests
    
    Returns:
        Fragility index (higher = more fragile)
    """
    if not sensitivity_results:
        return 0.0
    
    fragilities = []
    
    for test_name, result in sensitivity_results.items():
        if result.perturbation_size > 0:
            # Normalized fragility
            frag = abs(result.pnl_change_pct) / result.perturbation_size
            fragilities.append(frag)
    
    if not fragilities:
        return 0.0
    
    return np.mean(fragilities)


def assess_fragility(
    sensitivity_results: Dict[str, SensitivityResult],
    max_fragility: float = 0.35
) -> Dict[str, Any]:
    """
    Assess strategy fragility.
    
    Args:
        sensitivity_results: Sensitivity test results
        max_fragility: Maximum acceptable fragility
    
    Returns:
        Fragility assessment
    """
    fragility_index = compute_fragility_index(sensitivity_results)
    
    is_robust = fragility_index <= max_fragility
    
    # Identify most fragile dimension
    fragile_tests = {
        name: result
        for name, result in sensitivity_results.items()
        if not result.is_robust
    }
    
    most_fragile = None
    if fragile_tests:
        most_fragile = max(
            fragile_tests.items(),
            key=lambda x: abs(x[1].pnl_change_pct)
        )[0]
    
    return {
        'is_robust': is_robust,
        'fragility_index': fragility_index,
        'most_fragile_dimension': most_fragile,
        'fragile_tests': list(fragile_tests.keys()),
        'num_tests': len(sensitivity_results),
        'num_passed': sum(1 for r in sensitivity_results.values() if r.is_robust),
        'message': f"Fragility index: {fragility_index:.3f} (threshold: {max_fragility:.3f})"
    }


def compute_perturbation_amplification(
    sensitivity_results: Dict[str, SensitivityResult]
) -> float:
    """
    Compute how much perturbations are amplified.
    
    amplification = |PnL_change| / |input_change|
    
    Args:
        sensitivity_results: Sensitivity results
    
    Returns:
        Amplification factor
    """
    if not sensitivity_results:
        return 0.0
    
    amplifications = []
    
    for result in sensitivity_results.values():
        if result.perturbation_size > 0:
            amp = abs(result.pnl_change_pct) / result.perturbation_size
            amplifications.append(amp)
    
    return np.mean(amplifications) if amplifications else 0.0

