"""
Promotion Rules for Meridian v2.1.2

Defines criteria for promoting strategies through the incubation pipeline.
"""

from typing import Dict, Any, Tuple
from .incubator_state import StrategyState


def can_promote_to_paper(
    wfa_metrics: Dict[str, float],
    cfg: Any
) -> Tuple[bool, str]:
    """
    Check if strategy can be promoted from WFA to Paper Trading.
    
    Criteria:
    - WFA Sharpe >= threshold
    - WFA MAR >= threshold
    - Overfit ratio <= threshold
    - Win rate >= threshold
    - Stability score >= threshold
    
    Args:
        wfa_metrics: WFA metrics from Phase 20
        cfg: Configuration with thresholds
    
    Returns:
        (can_promote, reason)
    """
    # Check WFA Sharpe
    oos_sharpe = wfa_metrics.get('mean_oos_sharpe', 0.0)
    if oos_sharpe < cfg.incubation.min_wfa_sharpe:
        return False, f"OOS Sharpe {oos_sharpe:.2f} < {cfg.incubation.min_wfa_sharpe}"
    
    # Check overfit ratio
    overfit_idx = wfa_metrics.get('overfit_index', 999)
    if overfit_idx > cfg.incubation.max_wfa_overfit_ratio:
        return False, f"Overfit index {overfit_idx:.2f} > {cfg.incubation.max_wfa_overfit_ratio}"
    
    # Check win rate
    win_rate = wfa_metrics.get('win_rate', 0.0)
    if win_rate < cfg.incubation.min_wfa_winrate:
        return False, f"Win rate {win_rate:.2%} < {cfg.incubation.min_wfa_winrate:.2%}"
    
    # Check stability
    stability = wfa_metrics.get('stability_score', 0.0)
    if stability < cfg.incubation.min_wfa_stability:
        return False, f"Stability {stability:.2f} < {cfg.incubation.min_wfa_stability}"
    
    return True, "All WFA criteria met"


def can_promote_to_live(
    paper_metrics: Dict[str, float],
    days_in_paper: int,
    cfg: Any
) -> Tuple[bool, str]:
    """
    Check if strategy can be promoted from Paper to Live Trading.
    
    Criteria:
    - Minimum days in paper
    - Paper Sharpe >= threshold
    - Paper drawdown <= threshold
    - Consistency >= threshold
    
    Args:
        paper_metrics: Paper trading metrics
        days_in_paper: Days spent in paper trading
        cfg: Configuration
    
    Returns:
        (can_promote, reason)
    """
    # Check minimum days
    if days_in_paper < cfg.incubation.min_paper_days:
        return False, f"Only {days_in_paper} days in paper (need {cfg.incubation.min_paper_days})"
    
    # Check paper Sharpe
    paper_sharpe = paper_metrics.get('sharpe', 0.0)
    if paper_sharpe < cfg.incubation.min_paper_sharpe:
        return False, f"Paper Sharpe {paper_sharpe:.2f} < {cfg.incubation.min_paper_sharpe}"
    
    # Check drawdown
    paper_dd = paper_metrics.get('max_drawdown', 0.0)
    if paper_dd > cfg.incubation.max_paper_drawdown:
        return False, f"Paper DD {paper_dd:.2%} > {cfg.incubation.max_paper_drawdown:.2%}"
    
    # Manual approval required
    if cfg.incubation.require_manual_live_approval:
        return False, "Manual approval required for live promotion"
    
    return True, "All paper trading criteria met"


def evaluate_promotion(
    current_state: StrategyState,
    wfa_metrics: Dict[str, float],
    paper_metrics: Dict[str, float],
    days_in_state: int,
    cfg: Any
) -> Tuple[StrategyState, str]:
    """
    Evaluate if strategy should be promoted to next stage.
    
    Args:
        current_state: Current strategy state
        wfa_metrics: WFA results
        paper_metrics: Paper trading results
        days_in_state: Days in current state
        cfg: Configuration
    
    Returns:
        (new_state, reason)
    """
    if not cfg.incubation.allow_auto_promotion:
        return current_state, "Auto-promotion disabled"
    
    # Research → WFA_PASSED (manual trigger typically)
    if current_state == StrategyState.RESEARCH:
        return current_state, "Awaiting WFA completion"
    
    # WFA_PASSED → Paper Trading
    if current_state == StrategyState.WFA_PASSED:
        can_promote, reason = can_promote_to_paper(wfa_metrics, cfg)
        if can_promote:
            return StrategyState.PAPER_TRADING, "WFA passed, promoting to paper"
        else:
            return current_state, reason
    
    # Paper → Live
    if current_state == StrategyState.PAPER_TRADING:
        can_promote, reason = can_promote_to_live(paper_metrics, days_in_state, cfg)
        if can_promote:
            return StrategyState.LIVE_TRADING, "Paper passed, promoting to live"
        else:
            return current_state, reason
    
    # Already live or disabled
    return current_state, "No promotion applicable"


