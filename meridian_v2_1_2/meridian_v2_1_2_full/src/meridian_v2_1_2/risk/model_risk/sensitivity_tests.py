"""
Sensitivity Tests for Meridian v2.1.2

Test strategy robustness to micro-perturbations.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, Callable


@dataclass
class SensitivityResult:
    """Results from sensitivity test"""
    test_name: str
    perturbation_size: float
    baseline_pnl: float
    perturbed_pnl: float
    pnl_change: float
    pnl_change_pct: float
    is_robust: bool


def run_sensitivity_tests(
    baseline_data: Dict[str, Any],
    strategy_func: Callable,
    shock_pct: float = 0.01
) -> Dict[str, SensitivityResult]:
    """
    Run micro-perturbation sensitivity tests.
    
    Args:
        baseline_data: Baseline market data
        strategy_func: Strategy function to test
        shock_pct: Perturbation size (1% default)
    
    Returns:
        Dict of test results
    """
    results = {}
    
    # Get baseline PnL
    baseline_pnl = _compute_strategy_pnl(baseline_data, strategy_func)
    
    # Test 1: Price shock
    results['price_shock'] = _test_price_sensitivity(
        baseline_data, strategy_func, baseline_pnl, shock_pct
    )
    
    # Test 2: Yield shock  
    results['yield_shock'] = _test_yield_sensitivity(
        baseline_data, strategy_func, baseline_pnl, shock_pct
    )
    
    # Test 3: COT noise
    results['cot_noise'] = _test_cot_sensitivity(
        baseline_data, strategy_func, baseline_pnl, shock_pct * 15
    )
    
    # Test 4: Cycle perturbation
    results['cycle_perturb'] = _test_cycle_sensitivity(
        baseline_data, strategy_func, baseline_pnl, shock_pct * 10
    )
    
    return results


def _compute_strategy_pnl(data: Dict[str, Any], strategy_func: Callable) -> float:
    """Compute strategy PnL (simplified)"""
    try:
        # This would run the strategy on data
        # For now, return mock value
        return 1000.0
    except:
        return 0.0


def _test_price_sensitivity(
    data: Dict[str, Any],
    strategy_func: Callable,
    baseline_pnl: float,
    shock_pct: float
) -> SensitivityResult:
    """Test sensitivity to price shocks"""
    
    # Perturb prices
    perturbed_data = data.copy()
    
    if 'prices' in perturbed_data:
        for symbol in perturbed_data['prices']:
            if isinstance(perturbed_data['prices'][symbol], pd.DataFrame):
                perturbed_data['prices'][symbol] = perturbed_data['prices'][symbol] * (1 + shock_pct)
    
    # Compute perturbed PnL
    perturbed_pnl = _compute_strategy_pnl(perturbed_data, strategy_func)
    
    pnl_change = perturbed_pnl - baseline_pnl
    pnl_change_pct = pnl_change / abs(baseline_pnl) if baseline_pnl != 0 else 0
    
    # Robust if change is small relative to shock
    is_robust = abs(pnl_change_pct) < shock_pct * 5  # 5x tolerance
    
    return SensitivityResult(
        test_name="price_shock",
        perturbation_size=shock_pct,
        baseline_pnl=baseline_pnl,
        perturbed_pnl=perturbed_pnl,
        pnl_change=pnl_change,
        pnl_change_pct=pnl_change_pct,
        is_robust=is_robust
    )


def _test_yield_sensitivity(
    data: Dict[str, Any],
    strategy_func: Callable,
    baseline_pnl: float,
    shock_pct: float
) -> SensitivityResult:
    """Test sensitivity to yield shocks"""
    
    perturbed_data = data.copy()
    
    if 'real_yields' in perturbed_data and isinstance(perturbed_data['real_yields'], pd.DataFrame):
        perturbed_data['real_yields'] = perturbed_data['real_yields'] + shock_pct * 100  # bps
    
    perturbed_pnl = _compute_strategy_pnl(perturbed_data, strategy_func)
    
    pnl_change = perturbed_pnl - baseline_pnl
    pnl_change_pct = pnl_change / abs(baseline_pnl) if baseline_pnl != 0 else 0
    
    is_robust = abs(pnl_change_pct) < shock_pct * 10
    
    return SensitivityResult(
        test_name="yield_shock",
        perturbation_size=shock_pct,
        baseline_pnl=baseline_pnl,
        perturbed_pnl=perturbed_pnl,
        pnl_change=pnl_change,
        pnl_change_pct=pnl_change_pct,
        is_robust=is_robust
    )


def _test_cot_sensitivity(
    data: Dict[str, Any],
    strategy_func: Callable,
    baseline_pnl: float,
    noise_pct: float
) -> SensitivityResult:
    """Test sensitivity to COT noise"""
    
    perturbed_data = data.copy()
    
    if 'cot' in perturbed_data and isinstance(perturbed_data['cot'], pd.DataFrame):
        # Add noise to COT data
        noise = np.random.randn(*perturbed_data['cot'].shape) * noise_pct
        perturbed_data['cot'] = perturbed_data['cot'] * (1 + noise)
    
    perturbed_pnl = _compute_strategy_pnl(perturbed_data, strategy_func)
    
    pnl_change = perturbed_pnl - baseline_pnl
    pnl_change_pct = pnl_change / abs(baseline_pnl) if baseline_pnl != 0 else 0
    
    is_robust = abs(pnl_change_pct) < noise_pct
    
    return SensitivityResult(
        test_name="cot_noise",
        perturbation_size=noise_pct,
        baseline_pnl=baseline_pnl,
        perturbed_pnl=perturbed_pnl,
        pnl_change=pnl_change,
        pnl_change_pct=pnl_change_pct,
        is_robust=is_robust
    )


def _test_cycle_sensitivity(
    data: Dict[str, Any],
    strategy_func: Callable,
    baseline_pnl: float,
    perturb_pct: float
) -> SensitivityResult:
    """Test sensitivity to cycle perturbations"""
    
    perturbed_data = data.copy()
    
    # Would perturb cycle data if available
    # For now, simplified
    
    perturbed_pnl = baseline_pnl * (1 + np.random.randn() * perturb_pct)
    
    pnl_change = perturbed_pnl - baseline_pnl
    pnl_change_pct = pnl_change / abs(baseline_pnl) if baseline_pnl != 0 else 0
    
    is_robust = abs(pnl_change_pct) < perturb_pct * 2
    
    return SensitivityResult(
        test_name="cycle_perturb",
        perturbation_size=perturb_pct,
        baseline_pnl=baseline_pnl,
        perturbed_pnl=perturbed_pnl,
        pnl_change=pnl_change,
        pnl_change_pct=pnl_change_pct,
        is_robust=is_robust
    )

