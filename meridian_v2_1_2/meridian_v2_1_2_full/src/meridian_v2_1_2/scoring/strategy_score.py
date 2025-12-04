"""
Strategy Scoring Engine

Calculates composite robustness score from multiple dimensions:
- Performance metrics (Sharpe, return, drawdown)
- Monte Carlo uncertainty
- Walk-forward stability
- Risk-adjusted returns

Produces 0-100 score for strategy ranking and comparison.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class StrategyScore:
    """Complete strategy scoring results"""
    total_score: float  # Composite score (0-100)
    component_scores: Dict[str, float]  # Individual dimension scores
    weights: Dict[str, float]  # Weighting scheme used
    grade: str  # Letter grade (A+, A, B+, etc.)
    strengths: List[str]  # Areas of strength
    weaknesses: List[str]  # Areas needing improvement
    recommendation: str  # Overall assessment


# Default scoring weights (editable)
DEFAULT_WEIGHTS = {
    'performance': 0.30,  # Raw performance metrics
    'risk_adjusted': 0.25,  # Sharpe, Calmar ratios
    'robustness': 0.25,  # Monte Carlo, walk-forward
    'drawdown': 0.20,  # Drawdown control
}


def score_strategy(
    metrics: Dict[str, float],
    mc_stats: Optional[Dict[str, Any]] = None,
    wf_stats: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None
) -> StrategyScore:
    """
    Calculate comprehensive strategy score.
    
    Evaluates strategy across multiple dimensions and produces a
    composite 0-100 score for ranking and comparison.
    
    Args:
        metrics: Performance metrics dict (sharpe, return, drawdown, etc.)
        mc_stats: Monte Carlo simulation statistics (optional)
        wf_stats: Walk-forward validation statistics (optional)
        weights: Custom weighting scheme (optional, uses DEFAULT_WEIGHTS)
    
    Returns:
        StrategyScore: Complete scoring breakdown with recommendation
    
    Example:
        >>> metrics = {'sharpe_ratio': 1.5, 'total_return': 0.25, 'max_drawdown': -0.15}
        >>> mc_stats = {'risk_of_ruin': 0.05, 'downside_probability': 0.35}
        >>> score = score_strategy(metrics, mc_stats)
        >>> print(f"Score: {score.total_score:.1f} ({score.grade})")
        >>> print(f"Recommendation: {score.recommendation}")
    """
    
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    
    # Calculate component scores
    component_scores = {}
    
    # 1. Performance Score (raw returns)
    component_scores['performance'] = _score_performance(metrics)
    
    # 2. Risk-Adjusted Score (Sharpe, Calmar)
    component_scores['risk_adjusted'] = _score_risk_adjusted(metrics)
    
    # 3. Robustness Score (MC + WF stability)
    component_scores['robustness'] = _score_robustness(mc_stats, wf_stats)
    
    # 4. Drawdown Control Score
    component_scores['drawdown'] = _score_drawdown(metrics, mc_stats)
    
    # Calculate weighted total score
    total_score = sum(
        component_scores.get(component, 0) * weight
        for component, weight in weights.items()
    )
    
    # Ensure score is in 0-100 range
    total_score = max(0.0, min(100.0, total_score))
    
    # Assign letter grade
    grade = _assign_grade(total_score)
    
    # Identify strengths and weaknesses
    strengths, weaknesses = _identify_strengths_weaknesses(component_scores)
    
    # Generate recommendation
    recommendation = _generate_recommendation(
        total_score, 
        component_scores, 
        metrics, 
        mc_stats, 
        wf_stats
    )
    
    return StrategyScore(
        total_score=float(total_score),
        component_scores=component_scores,
        weights=weights,
        grade=grade,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendation=recommendation
    )


def calculate_composite_score(
    performance: float,
    risk_adjusted: float,
    robustness: float,
    drawdown: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate weighted composite score from components.
    
    Args:
        performance: Performance score (0-100)
        risk_adjusted: Risk-adjusted score (0-100)
        robustness: Robustness score (0-100)
        drawdown: Drawdown score (0-100)
        weights: Custom weights (optional)
    
    Returns:
        Composite score (0-100)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    
    components = {
        'performance': performance,
        'risk_adjusted': risk_adjusted,
        'robustness': robustness,
        'drawdown': drawdown
    }
    
    total = sum(components[k] * weights.get(k, 0) for k in components.keys())
    return max(0.0, min(100.0, total))


def rank_strategies(scores: List[StrategyScore]) -> List[Tuple[int, StrategyScore]]:
    """
    Rank multiple strategies by score.
    
    Args:
        scores: List of StrategyScore objects
    
    Returns:
        List of (rank, score) tuples, sorted best to worst
    """
    sorted_scores = sorted(scores, key=lambda s: s.total_score, reverse=True)
    return [(i + 1, score) for i, score in enumerate(sorted_scores)]


# ============================================================================
# COMPONENT SCORING FUNCTIONS
# ============================================================================

def _score_performance(metrics: Dict[str, float]) -> float:
    """Score based on raw returns (0-100)"""
    total_return = metrics.get('total_return', 0)
    
    # Map return to 0-100 scale
    # 0% return = 0, 100% return = 100, 50% = 75
    if total_return <= 0:
        return 0.0
    elif total_return >= 1.0:  # 100%+ return
        return 100.0
    else:
        # Logarithmic scaling favors higher returns
        return min(100.0, 75 + 25 * np.log10(1 + total_return * 9))


def _score_risk_adjusted(metrics: Dict[str, float]) -> float:
    """Score based on Sharpe ratio and Calmar ratio (0-100)"""
    sharpe = metrics.get('sharpe_ratio', 0)
    calmar = metrics.get('calmar_ratio', 0)
    
    # Sharpe scoring: 0 = 0, 1 = 50, 2 = 75, 3+ = 100
    if sharpe <= 0:
        sharpe_score = 0
    elif sharpe >= 3.0:
        sharpe_score = 100
    else:
        sharpe_score = (sharpe / 3.0) ** 0.7 * 100
    
    # Calmar scoring: similar scale
    if calmar <= 0:
        calmar_score = 0
    elif calmar >= 3.0:
        calmar_score = 100
    else:
        calmar_score = (calmar / 3.0) ** 0.7 * 100
    
    # Weighted average (Sharpe is primary)
    return 0.7 * sharpe_score + 0.3 * calmar_score


def _score_robustness(
    mc_stats: Optional[Dict[str, Any]], 
    wf_stats: Optional[Dict[str, Any]]
) -> float:
    """Score based on Monte Carlo and walk-forward stability (0-100)"""
    
    mc_score = 50.0  # Default if not available
    wf_score = 50.0
    
    # Monte Carlo scoring
    if mc_stats:
        risk_of_ruin = mc_stats.get('risk_of_ruin', 0.5)
        downside_prob = mc_stats.get('downside_probability', 0.5)
        
        # Lower risk of ruin is better
        mc_score = (1 - risk_of_ruin) * 100
        
        # Adjust for downside probability
        mc_score *= (1 - downside_prob * 0.5)
    
    # Walk-forward scoring
    if wf_stats:
        stability = wf_stats.get('stability_score', 50)
        degradation = wf_stats.get('degradation_factor', 0.7)
        
        # Use stability score directly
        wf_score = stability
        
        # Penalize if degradation is severe (test << train)
        if degradation < 0.5:
            wf_score *= 0.5
        elif degradation < 0.7:
            wf_score *= 0.8
    
    # Average if both available, or use whichever is available
    if mc_stats and wf_stats:
        return (mc_score + wf_score) / 2
    elif mc_stats:
        return mc_score
    elif wf_stats:
        return wf_score
    else:
        return 50.0  # No data available


def _score_drawdown(
    metrics: Dict[str, float], 
    mc_stats: Optional[Dict[str, Any]]
) -> float:
    """Score based on drawdown control (0-100)"""
    max_dd = abs(metrics.get('max_drawdown', 0.5))
    
    # Base drawdown score
    # 0-5% DD = 100, 5-10% = 85, 10-20% = 70, 20-30% = 50, 30%+ = 25
    if max_dd <= 0.05:
        dd_score = 100
    elif max_dd <= 0.10:
        dd_score = 85
    elif max_dd <= 0.20:
        dd_score = 70
    elif max_dd <= 0.30:
        dd_score = 50
    else:
        dd_score = max(0, 50 - (max_dd - 0.30) * 100)
    
    # Adjust for Monte Carlo worst-case if available
    if mc_stats:
        worst_dd = abs(mc_stats.get('worst_drawdown', max_dd))
        if worst_dd > max_dd * 1.5:  # Worst case is much worse
            dd_score *= 0.8
    
    return dd_score


def _assign_grade(score: float) -> str:
    """Convert numerical score to letter grade"""
    if score >= 95:
        return 'A+'
    elif score >= 90:
        return 'A'
    elif score >= 85:
        return 'A-'
    elif score >= 80:
        return 'B+'
    elif score >= 75:
        return 'B'
    elif score >= 70:
        return 'B-'
    elif score >= 65:
        return 'C+'
    elif score >= 60:
        return 'C'
    elif score >= 55:
        return 'C-'
    elif score >= 50:
        return 'D+'
    elif score >= 45:
        return 'D'
    else:
        return 'F'


def _identify_strengths_weaknesses(
    component_scores: Dict[str, float]
) -> Tuple[List[str], List[str]]:
    """Identify top strengths and weaknesses"""
    strengths = []
    weaknesses = []
    
    for component, score in component_scores.items():
        if score >= 80:
            strengths.append(f"{component.replace('_', ' ').title()} (Score: {score:.0f})")
        elif score < 60:
            weaknesses.append(f"{component.replace('_', ' ').title()} (Score: {score:.0f})")
    
    return strengths, weaknesses


def _generate_recommendation(
    total_score: float,
    component_scores: Dict[str, float],
    metrics: Dict[str, float],
    mc_stats: Optional[Dict[str, Any]],
    wf_stats: Optional[Dict[str, Any]]
) -> str:
    """Generate human-readable recommendation"""
    
    if total_score >= 85:
        base = "Excellent strategy with strong performance across all dimensions."
    elif total_score >= 70:
        base = "Good strategy with solid fundamentals."
    elif total_score >= 55:
        base = "Acceptable strategy but needs improvement."
    else:
        base = "Strategy requires significant optimization."
    
    # Add specific recommendations
    suggestions = []
    
    if component_scores.get('drawdown', 100) < 60:
        suggestions.append("Consider tightening stop-losses or risk parameters.")
    
    if component_scores.get('robustness', 100) < 60:
        suggestions.append("Strategy may be overfitted - consider simplifying or using longer lookback periods.")
    
    if mc_stats and mc_stats.get('risk_of_ruin', 0) > 0.10:
        suggestions.append("High risk of ruin detected - reduce position sizes.")
    
    if wf_stats and wf_stats.get('degradation_factor', 1.0) < 0.7:
        suggestions.append("Significant performance degradation in out-of-sample testing - review parameter selection.")
    
    if suggestions:
        return base + " " + " ".join(suggestions)
    else:
        return base + " Continue monitoring performance."


