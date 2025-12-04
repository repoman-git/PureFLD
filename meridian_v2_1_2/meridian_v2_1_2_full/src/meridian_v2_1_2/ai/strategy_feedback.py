"""
AI Strategy Feedback Layer

Rule-based coaching system for strategy refinement.
Provides specific, actionable feedback based on performance analysis.
Ready for LLM integration in future phases.
"""

from typing import Dict, Any, List


def ai_feedback(
    metrics: Dict[str, float],
    mc_stats: Dict[str, Any] = None,
    wf_stats: Dict[str, Any] = None
) -> List[str]:
    """
    Generate AI-like feedback suggestions (rule-based).
    
    NO LLMs - purely heuristic rules that mimic expert trader advice.
    Future: Can feed these into GPT/Claude for enhanced suggestions.
    
    Args:
        metrics: Strategy performance metrics
        mc_stats: Monte Carlo statistics (optional)
        wf_stats: Walk-forward statistics (optional)
    
    Returns:
        List of actionable feedback strings
    
    Example:
        >>> metrics = {'max_drawdown': -0.30, 'sharpe_ratio': 0.8}
        >>> feedback = ai_feedback(metrics)
        >>> for suggestion in feedback:
        ...     print(f"💡 {suggestion}")
    """
    
    suggestions = []
    
    # Extract metrics
    sharpe = metrics.get('sharpe_ratio', 0)
    max_dd = abs(metrics.get('max_drawdown', 0))
    total_return = metrics.get('total_return', 0)
    win_rate = metrics.get('win_rate', 0.5)
    volatility = metrics.get('volatility', 0)
    
    # ==== DRAWDOWN FEEDBACK ====
    if max_dd > 0.25:
        suggestions.append(
            "🔴 Drawdown > 25%: Reduce displacement or add filter. "
            "Consider scaling position size inversely with recent volatility."
        )
    elif max_dd > 0.15:
        suggestions.append(
            "🟡 Drawdown 15-25%: Within acceptable range but could be improved. "
            "Try tightening stop-losses or adding a volatility regime filter."
        )
    
    # ==== SHARPE RATIO FEEDBACK ====
    if sharpe < 0.5:
        suggestions.append(
            "🔴 Sharpe < 0.5: Strategy lacks edge. "
            "Consider: (1) Inverting signals, (2) Adding confirmation filters, "
            "(3) Reducing trade frequency to capture only high-quality setups."
        )
    elif sharpe < 1.0:
        suggestions.append(
            "🟡 Sharpe < 1.0: Marginal risk-adjusted returns. "
            "Increase signal quality over quantity. Try longer cycle lengths or stricter COT thresholds."
        )
    elif sharpe > 2.0:
        suggestions.append(
            "✅ Sharpe > 2.0: Excellent! But verify with walk-forward to avoid overfitting. "
            "This level of performance may not persist out-of-sample."
        )
    
    # ==== RETURN FEEDBACK ====
    if total_return < 0:
        suggestions.append(
            "🔴 Negative returns: Strategy is losing money. "
            "Check if signals are inverted or if market regime has fundamentally changed."
        )
    elif total_return < 0.10 and sharpe > 0:
        suggestions.append(
            "🟡 Low absolute returns: Strategy is cautious. "
            "Consider increasing position size or reducing filter strictness if Sharpe is good."
        )
    
    # ==== WIN RATE FEEDBACK ====
    if win_rate < 0.35:
        suggestions.append(
            "🔴 Win rate < 35%: Very low hit rate. "
            "Either winners must be huge (verify profit factor > 2.0) or strategy needs better timing."
        )
    elif win_rate < 0.45:
        suggestions.append(
            "🟡 Win rate < 45%: Below average. "
            "Improve entry timing or add confirmation indicators to filter weak signals."
        )
    elif win_rate > 0.65 and sharpe < 1.0:
        suggestions.append(
            "⚠️  High win rate but low Sharpe: Winners may be too small. "
            "Let winning trades run longer or reduce stop-losses."
        )
    
    # ==== VOLATILITY FEEDBACK ====
    if volatility > 0.30:
        suggestions.append(
            "🟡 High volatility (>30%): Strategy is choppy. "
            "Add volatility targeting or reduce leverage during high-vol regimes."
        )
    
    # ==== MONTE CARLO FEEDBACK ====
    if mc_stats:
        risk_of_ruin = mc_stats.get('risk_of_ruin', 0)
        downside_prob = mc_stats.get('downside_probability', 0)
        
        if risk_of_ruin > 0.20:
            suggestions.append(
                "🔴 MC: Risk of ruin > 20%! Unacceptable. "
                "Drastically reduce position sizes or stop trading this strategy."
            )
        elif risk_of_ruin > 0.10:
            suggestions.append(
                "🟡 MC: Risk of ruin > 10%. Consider this high risk. "
                "Reduce position sizes by 30-50%."
            )
        
        if downside_prob > 0.50:
            suggestions.append(
                "🟡 MC: >50% chance of loss in simulations. "
                "Strategy edge may be weak. Add trend or seasonal filters."
            )
    
    # ==== WALK-FORWARD FEEDBACK ====
    if wf_stats:
        stability = wf_stats.get('stability_score', 100)
        degradation = wf_stats.get('degradation_factor', 1.0)
        
        if stability < 40:
            suggestions.append(
                "🔴 WF: Stability < 40. Strategy is wildly inconsistent. "
                "Likely overfitted. Use adaptive parameters or simpler logic."
            )
        elif stability < 60:
            suggestions.append(
                "🟡 WF: Stability < 60. Performance varies across periods. "
                "Consider regime-adaptive parameters or longer lookback periods."
            )
        
        if degradation < 0.50:
            suggestions.append(
                "🔴 WF: Test performance < 50% of train performance. "
                "Strong overfitting detected. Simplify or use regularization."
            )
        elif degradation < 0.70:
            suggestions.append(
                "🟡 WF: Moderate out-of-sample degradation. "
                "Increase training data size or reduce parameter complexity."
            )
    
    # ==== POSITIVE FEEDBACK ====
    if not suggestions and sharpe > 1.5 and max_dd < 0.15:
        suggestions.append(
            "✅ Strategy looks solid! Sharpe > 1.5 and drawdown < 15%. "
            "Continue monitoring and consider live paper trading."
        )
    
    # ==== ADAPTIVE SUGGESTIONS ====
    # If high Sharpe but high drawdown
    if sharpe > 1.5 and max_dd > 0.20:
        suggestions.append(
            "⚡ High Sharpe but large drawdown: You have edge but risk is high. "
            "Reduce leverage while maintaining signal logic."
        )
    
    # If low Sharpe but low drawdown
    if sharpe < 1.0 and max_dd < 0.10 and total_return > 0:
        suggestions.append(
            "💤 Conservative strategy: Low risk but limited returns. "
            "Increase aggressiveness if risk tolerance allows."
        )
    
    return suggestions if suggestions else ["✅ No critical issues detected."]


def critique_candidate(candidate: Dict[str, Any]) -> str:
    """
    Generate critique of a single candidate strategy.
    
    Args:
        candidate: Dictionary with params, metrics, fitness
    
    Returns:
        Human-readable critique string
    """
    params = candidate.get('params', {})
    metrics = candidate.get('metrics', {})
    fitness = candidate.get('fitness', 0)
    
    critique = []
    critique.append(f"**Fitness Score:** {fitness:.2f}")
    critique.append(f"**Parameters:** {params}")
    
    sharpe = metrics.get('sharpe_ratio', 0)
    total_return = metrics.get('total_return', 0)
    max_dd = abs(metrics.get('max_drawdown', 0))
    
    critique.append(f"**Performance:** Sharpe {sharpe:.2f}, Return {total_return:.1%}, DD {max_dd:.1%}")
    
    # Quick assessment
    if fitness > 50:
        critique.append("✅ **Assessment:** Strong candidate worth considering.")
    elif fitness > 30:
        critique.append("⚠️  **Assessment:** Decent but needs refinement.")
    else:
        critique.append("❌ **Assessment:** Weak candidate, consider discarding.")
    
    return "\n".join(critique)


