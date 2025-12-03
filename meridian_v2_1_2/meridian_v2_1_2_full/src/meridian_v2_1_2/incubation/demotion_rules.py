"""
Demotion Rules for Meridian v2.1.2

Defines criteria for demoting or disabling strategies.
"""

from typing import Dict, Any, Tuple
from .incubator_state import StrategyState


def should_demote_to_disabled(
    live_metrics: Dict[str, float],
    health_status: Dict[str, Any],
    cfg: Any
) -> Tuple[bool, str]:
    """
    Check if live strategy should be disabled.
    
    Triggers:
    - Drawdown breach
    - Consecutive failures
    - Health engine failures
    - Drift instability
    
    Args:
        live_metrics: Live trading metrics
        health_status: Health engine status
        cfg: Configuration
    
    Returns:
        (should_demote, reason)
    """
    # Check drawdown
    drawdown = live_metrics.get('max_drawdown', 0.0)
    if drawdown > cfg.incubation.max_live_drawdown:
        return True, f"Drawdown {drawdown:.2%} > {cfg.incubation.max_live_drawdown:.2%} - KILL SWITCH"
    
    # Check Sharpe degradation
    sharpe = live_metrics.get('sharpe', 0.0)
    if sharpe < cfg.incubation.min_live_sharpe:
        return True, f"Sharpe {sharpe:.2f} < {cfg.incubation.min_live_sharpe}"
    
    # Check health status
    if health_status.get('status') == 'FAIL':
        consecutive_fails = health_status.get('consecutive_failures', 0)
        if consecutive_fails >= cfg.incubation.consecutive_failures_limit:
            return True, f"Health failures: {consecutive_fails} consecutive"
    
    # Check drift
    drift = live_metrics.get('position_drift_pct', 0.0)
    if drift > cfg.incubation.max_live_drift_pct:
        return True, f"Position drift {drift:.2%} > {cfg.incubation.max_live_drift_pct:.2%}"
    
    return False, "No demotion triggers"


def should_demote_to_paper(
    live_metrics: Dict[str, float],
    cfg: Any
) -> Tuple[bool, str]:
    """
    Check if live strategy should be demoted to paper (not disabled).
    
    This is a softer demotion for performance degradation.
    
    Args:
        live_metrics: Live metrics
        cfg: Configuration
    
    Returns:
        (should_demote, reason)
    """
    # Moderate Sharpe decline
    sharpe = live_metrics.get('sharpe', 0.0)
    if cfg.incubation.min_live_sharpe < sharpe < cfg.incubation.min_paper_sharpe:
        return True, f"Sharpe declined to {sharpe:.2f}, moving back to paper"
    
    return False, "No soft demotion needed"


def evaluate_demotion(
    current_state: StrategyState,
    live_metrics: Dict[str, float],
    health_status: Dict[str, Any],
    cfg: Any
) -> Tuple[StrategyState, str]:
    """
    Evaluate if strategy should be demoted.
    
    Args:
        current_state: Current state
        live_metrics: Live trading metrics
        health_status: Health engine status
        cfg: Configuration
    
    Returns:
        (new_state, reason)
    """
    if not cfg.incubation.allow_auto_demotion:
        return current_state, "Auto-demotion disabled"
    
    # Only applies to live strategies
    if current_state != StrategyState.LIVE_TRADING:
        return current_state, "Not in live trading"
    
    # Check for hard demotion (disable)
    should_disable, reason = should_demote_to_disabled(live_metrics, health_status, cfg)
    if should_disable:
        return StrategyState.DISABLED, reason
    
    # Check for soft demotion (back to paper)
    should_demote, reason = should_demote_to_paper(live_metrics, cfg)
    if should_demote:
        return StrategyState.PAPER_TRADING, reason
    
    return current_state, "No demotion needed"

