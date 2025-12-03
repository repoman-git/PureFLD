"""
Stress Test Runner for Meridian v2.1.2

Orchestrates chaos engineering runs.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..config import MeridianConfig
from ..synthetic import SyntheticDataset
from . import chaos_injector
from . import market_shocks


@dataclass
class StressTestResult:
    """Results from a single stress test run"""
    
    run_id: int
    scenario_name: str
    severity: float
    
    # System behavior
    completed: bool = False
    crashed: bool = False
    kill_switch_triggered: bool = False
    
    # Failures injected
    injected_failures: List[str] = field(default_factory=list)
    
    # Metrics
    final_equity: float = 0.0
    max_drawdown: float = 0.0
    position_drift: float = 0.0
    oms_errors: int = 0
    nan_count: int = 0
    
    # Error messages
    error_messages: List[str] = field(default_factory=list)
    
    # Weakness flags
    weaknesses: List[str] = field(default_factory=list)


def run_stress_tests(
    config: MeridianConfig,
    num_runs: int = None,
    scenarios: List[str] = None
) -> List[StressTestResult]:
    """
    Run comprehensive stress tests.
    
    Args:
        config: Meridian configuration
        num_runs: Number of test runs (overrides config)
        scenarios: Specific scenarios to run
    
    Returns:
        List of stress test results
    """
    if num_runs is None:
        num_runs = config.stress.num_runs
    
    if scenarios is None:
        scenarios = [
            'baseline',
            'price_gaps',
            'missing_bars',
            'nan_bursts',
            'vol_explosion',
            'flash_crash',
            'rate_shock',
            'cycle_inversion',
            'regime_whiplash',
            'correlation_break',
            'combined_chaos'
        ]
    
    results = []
    
    for run_id in range(num_runs):
        # Select random scenario
        scenario = np.random.choice(scenarios)
        
        # Run test
        result = _run_single_stress_test(
            run_id=run_id,
            scenario=scenario,
            config=config
        )
        
        results.append(result)
    
    return results


def _run_single_stress_test(
    run_id: int,
    scenario: str,
    config: MeridianConfig
) -> StressTestResult:
    """
    Run a single stress test.
    
    Args:
        run_id: Test run ID
        scenario: Scenario name
        config: Configuration
    
    Returns:
        Test result
    """
    result = StressTestResult(
        run_id=run_id,
        scenario_name=scenario,
        severity=config.stress.severity
    )
    
    try:
        # Generate synthetic data
        dataset = SyntheticDataset(config)
        data = dataset.generate(symbols=['GLD', 'LTPZ'])
        
        # Apply chaos based on scenario
        data = _apply_scenario(scenario, data, config)
        
        # Track what was injected
        result.injected_failures = _get_injected_failures(scenario)
        
        # Run mini pipeline simulation
        pipeline_result = _simulate_pipeline(data, config)
        
        result.completed = pipeline_result.get('completed', False)
        result.final_equity = pipeline_result.get('final_equity', 0.0)
        result.max_drawdown = pipeline_result.get('max_drawdown', 0.0)
        result.position_drift = pipeline_result.get('position_drift', 0.0)
        result.oms_errors = pipeline_result.get('oms_errors', 0)
        result.kill_switch_triggered = pipeline_result.get('kill_switch', False)
        
        # Count NaNs in data
        result.nan_count = _count_nans(data)
        
        # Identify weaknesses
        result.weaknesses = _identify_weaknesses(result, data)
        
    except Exception as e:
        result.crashed = True
        result.error_messages.append(str(e))
    
    return result


def _apply_scenario(
    scenario: str,
    data: Dict[str, Any],
    config: MeridianConfig
) -> Dict[str, Any]:
    """Apply chaos scenario to data"""
    
    severity = config.stress.severity
    
    if scenario == 'baseline':
        # No chaos
        return data
    
    elif scenario == 'price_gaps':
        for symbol in data['prices']:
            data['prices'][symbol] = chaos_injector.inject_price_gaps(
                data['prices'][symbol],
                severity=severity
            )
    
    elif scenario == 'missing_bars':
        for symbol in data['prices']:
            data['prices'][symbol] = chaos_injector.inject_missing_bars(
                data['prices'][symbol],
                severity=severity
            )
    
    elif scenario == 'nan_bursts':
        for symbol in data['prices']:
            data['prices'][symbol] = chaos_injector.inject_nan_bursts(
                data['prices'][symbol],
                severity=severity
            )
    
    elif scenario == 'vol_explosion':
        shock_day = len(data['prices']['GLD']) // 2
        for symbol in data['prices']:
            data['prices'][symbol] = market_shocks.volatility_explosion(
                data['prices'][symbol],
                shock_day=shock_day,
                magnitude=2.0 + severity
            )
    
    elif scenario == 'flash_crash':
        crash_day = len(data['prices']['GLD']) // 2
        for symbol in data['prices']:
            data['prices'][symbol] = market_shocks.flash_crash(
                data['prices'][symbol],
                crash_day=crash_day,
                drop_pct=0.10 * severity
            )
    
    elif scenario == 'rate_shock':
        shock_day = len(data['real_yields']) // 2
        data['real_yields'] = market_shocks.rate_shock(
            data['real_yields'],
            shock_day=shock_day,
            spike_bps=100 * severity
        )
    
    elif scenario == 'cycle_inversion':
        # Would need cycle data - simulate by corrupting regime
        data['regimes'] = chaos_injector.inject_regime_corruption(
            data['regimes'],
            severity=severity
        )
    
    elif scenario == 'regime_whiplash':
        whiplash_start = len(data['regimes']) // 2
        data['regimes'] = market_shocks.regime_whiplash(
            data['regimes'],
            whiplash_start=whiplash_start,
            whiplash_days=int(20 * severity)
        )
    
    elif scenario == 'correlation_break':
        data['prices'] = chaos_injector.inject_correlation_breaks(
            data['prices'],
            severity=severity
        )
    
    elif scenario == 'combined_chaos':
        # Apply multiple chaos types
        for symbol in data['prices']:
            data['prices'][symbol] = chaos_injector.inject_price_gaps(
                data['prices'][symbol], severity=severity * 0.5
            )
            data['prices'][symbol] = chaos_injector.inject_nan_bursts(
                data['prices'][symbol], severity=severity * 0.3
            )
        
        data['regimes'] = chaos_injector.inject_regime_corruption(
            data['regimes'], severity=severity * 0.5
        )
    
    return data


def _get_injected_failures(scenario: str) -> List[str]:
    """Get list of failures injected"""
    failure_map = {
        'baseline': [],
        'price_gaps': ['price_gaps'],
        'missing_bars': ['missing_data'],
        'nan_bursts': ['nan_corruption'],
        'vol_explosion': ['vol_shock'],
        'flash_crash': ['flash_crash'],
        'rate_shock': ['yield_spike'],
        'cycle_inversion': ['cycle_break'],
        'regime_whiplash': ['regime_corruption'],
        'correlation_break': ['correlation_inversion'],
        'combined_chaos': ['multiple_failures']
    }
    
    return failure_map.get(scenario, [])


def _simulate_pipeline(
    data: Dict[str, Any],
    config: MeridianConfig
) -> Dict[str, Any]:
    """Simulate mini trading pipeline"""
    
    from ..execution.paper_sim import SimulatedBroker, SimulatedPerformance
    
    try:
        broker = SimulatedBroker(config=config)
        perf = SimulatedPerformance()
        
        # Simulate 10 days
        num_days = min(10, len(data['prices']['GLD']))
        
        for day in range(num_days):
            # Skip if data corrupted
            if day >= len(data['prices']['GLD']):
                break
            
            current_prices = {}
            for symbol in data['prices']:
                if day < len(data['prices'][symbol]):
                    close_price = data['prices'][symbol]['close'].iloc[day]
                    # Handle NaNs
                    if pd.isna(close_price):
                        close_price = 100.0  # Fallback
                    current_prices[symbol] = close_price
            
            # Simple trading
            if day == 2:
                broker.submit_order('GLD', 5.0, 'buy')
            
            # Update broker
            if day > 0:
                next_opens = {s: current_prices[s] * 1.001 for s in current_prices}
                broker.generate_fills(current_prices, next_opens)
            
            broker.update_market_values(current_prices)
            portfolio = broker.get_positions()
            perf.update(f"day_{day}", portfolio['equity'])
        
        # Compute metrics
        metrics = perf.get_metrics()
        
        return {
            'completed': True,
            'final_equity': portfolio['equity'],
            'max_drawdown': metrics.get('max_drawdown', 0.0),
            'position_drift': 0.0,  # Would compute from reconciliation
            'oms_errors': 0,
            'kill_switch': False
        }
    
    except Exception as e:
        return {
            'completed': False,
            'final_equity': 0.0,
            'max_drawdown': 1.0,
            'position_drift': 1.0,
            'oms_errors': 1,
            'kill_switch': True,
            'error': str(e)
        }


def _count_nans(data: Dict[str, Any]) -> int:
    """Count total NaNs in data"""
    nan_count = 0
    
    for symbol in data.get('prices', {}):
        nan_count += data['prices'][symbol].isna().sum().sum()
    
    if 'cot' in data:
        nan_count += data['cot'].isna().sum().sum()
    
    if 'real_yields' in data:
        nan_count += data['real_yields'].isna().sum().sum()
    
    return nan_count


def _identify_weaknesses(
    result: StressTestResult,
    data: Dict[str, Any]
) -> List[str]:
    """Identify system weaknesses"""
    weaknesses = []
    
    if result.crashed:
        weaknesses.append("SYSTEM_CRASH")
    
    if result.kill_switch_triggered:
        weaknesses.append("KILL_SWITCH_ACTIVATION")
    
    if result.nan_count > 100:
        weaknesses.append("NAN_SENSITIVITY")
    
    if result.max_drawdown > 0.20:
        weaknesses.append("HIGH_DRAWDOWN_UNDER_STRESS")
    
    if result.position_drift > 0.10:
        weaknesses.append("POSITION_DRIFT_EXPLOSION")
    
    if result.oms_errors > 0:
        weaknesses.append("OMS_FAILURE")
    
    if not result.completed:
        weaknesses.append("INCOMPLETE_EXECUTION")
    
    return weaknesses

