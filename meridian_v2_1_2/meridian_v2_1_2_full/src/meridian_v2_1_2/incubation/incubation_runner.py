"""
Incubation Runner for Meridian v2.1.2

Daily evaluation and state management for strategy lifecycle.
"""

from typing import Dict, Any
from .incubator_state import StrategyState, StrategyStatus, load_strategy_state, save_strategy_state
from .promotion_rules import evaluate_promotion
from .demotion_rules import evaluate_demotion


def update_strategy_state(
    strategy_name: str,
    wfa_metrics: Dict[str, float],
    paper_metrics: Dict[str, float],
    live_metrics: Dict[str, float],
    health_status: Dict[str, Any],
    cfg: Any,
    state_path: str = "state/strategy_status.json"
) -> StrategyStatus:
    """
    Update strategy state based on performance metrics.
    
    This is the core of the incubation engine, run daily.
    
    Args:
        strategy_name: Strategy identifier
        wfa_metrics: Walk-forward analysis results
        paper_metrics: Paper trading results
        live_metrics: Live trading results
        health_status: Health engine status
        cfg: Configuration
        state_path: Path to state file
    
    Returns:
        Updated StrategyStatus
    """
    # Load current state
    status = load_strategy_state(strategy_name, state_path)
    
    # Increment days in state
    status.days_in_state += 1
    
    # Store current metrics
    status.metadata['wfa_metrics'] = wfa_metrics
    status.metadata['paper_metrics'] = paper_metrics
    status.metadata['live_metrics'] = live_metrics
    status.metadata['health_status'] = health_status
    
    current_state = status.state
    
    # Evaluate demotion (takes priority)
    new_state, reason = evaluate_demotion(
        current_state,
        live_metrics,
        health_status,
        cfg
    )
    
    # If no demotion, evaluate promotion
    if new_state == current_state:
        new_state, reason = evaluate_promotion(
            current_state,
            wfa_metrics,
            paper_metrics,
            status.days_in_state,
            cfg
        )
    
    # Update state if changed
    if new_state != current_state:
        status.state = new_state
        status.days_in_state = 0
        status.metadata['transition_reason'] = reason
    
    # Save
    save_strategy_state(status, state_path)
    
    return status


def run_incubation_cycle(
    strategy_name: str,
    wfa_metrics: Dict[str, float],
    paper_metrics: Dict[str, float],
    live_metrics: Dict[str, float],
    health_status: Dict[str, Any],
    cfg: Any
) -> Dict[str, Any]:
    """
    Run complete incubation cycle for a strategy.
    
    This is called after EOD pipeline completes.
    
    Args:
        strategy_name: Strategy name
        wfa_metrics: WFA results
        paper_metrics: Paper results
        live_metrics: Live results
        health_status: Health status
        cfg: Configuration
    
    Returns:
        Dict with cycle results
    """
    # Update state
    status = update_strategy_state(
        strategy_name,
        wfa_metrics,
        paper_metrics,
        live_metrics,
        health_status,
        cfg
    )
    
    return {
        'strategy_name': strategy_name,
        'current_state': status.state.value,
        'days_in_state': status.days_in_state,
        'last_transition': status.last_transition,
        'transition_reason': status.metadata.get('transition_reason', 'N/A')
    }


