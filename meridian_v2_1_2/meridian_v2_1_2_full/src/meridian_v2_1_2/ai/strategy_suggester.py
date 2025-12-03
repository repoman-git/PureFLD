"""
AI Strategy Suggester

Rule-based strategy improvement suggestions based on metrics analysis.
Scaffolding ready for LLM integration (GPT-4, Claude, etc.) in future phases.

This module analyzes strategy performance and suggests specific improvements
without requiring external API calls.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ImprovementSuggestion:
    """Single improvement suggestion"""
    category: str  # 'risk', 'parameters', 'filters', 'stability'
    priority: str  # 'high', 'medium', 'low'
    title: str  # Short description
    description: str  # Detailed explanation
    action: str  # Specific action to take


def suggest_strategy_improvements(
    metrics: Dict[str, float],
    mc_stats: Optional[Dict[str, Any]] = None,
    wf_stats: Optional[Dict[str, Any]] = None
) -> List[ImprovementSuggestion]:
    """
    Generate rule-based improvement suggestions for strategy.
    
    Analyzes performance metrics, Monte Carlo results, and walk-forward
    validation to identify specific areas for improvement.
    
    Args:
        metrics: Strategy performance metrics
        mc_stats: Monte Carlo simulation statistics (optional)
        wf_stats: Walk-forward validation statistics (optional)
    
    Returns:
        List of ranked improvement suggestions
    
    Example:
        >>> metrics = {'sharpe_ratio': 0.8, 'max_drawdown': -0.35}
        >>> suggestions = suggest_strategy_improvements(metrics)
        >>> for sug in suggestions:
        ...     print(f"[{sug.priority.upper()}] {sug.title}")
        ...     print(f"  Action: {sug.action}")
    """
    
    suggestions = []
    
    # Analyze drawdown
    max_dd = abs(metrics.get('max_drawdown', 0))
    if max_dd > 0.25:  # >25% drawdown
        suggestions.append(ImprovementSuggestion(
            category='risk',
            priority='high',
            title='Excessive Drawdown Detected',
            description=f'Maximum drawdown of {max_dd:.1%} exceeds recommended threshold of 25%. '
                       'Large drawdowns can be psychologically difficult and may indicate '
                       'insufficient risk management.',
            action='Implement tighter stop-losses, reduce position sizing, or add volatility filters.'
        ))
    
    # Analyze Sharpe ratio
    sharpe = metrics.get('sharpe_ratio', 0)
    if sharpe < 1.0 and sharpe > 0:
        suggestions.append(ImprovementSuggestion(
            category='parameters',
            priority='medium',
            title='Low Risk-Adjusted Returns',
            description=f'Sharpe ratio of {sharpe:.2f} is below 1.0, indicating returns are not '
                       'sufficiently compensating for risk taken.',
            action='Consider: (1) Increasing signal strength thresholds, '
                   '(2) Adding confirmatory indicators, (3) Reducing trading frequency.'
        ))
    elif sharpe < 0:
        suggestions.append(ImprovementSuggestion(
            category='parameters',
            priority='high',
            title='Negative Risk-Adjusted Returns',
            description='Strategy has negative Sharpe ratio - losing money after adjusting for risk.',
            action='Major parameter revision needed. Consider inverting signals or complete redesign.'
        ))
    
    # Analyze Monte Carlo results
    if mc_stats:
        risk_of_ruin = mc_stats.get('risk_of_ruin', 0)
        if risk_of_ruin > 0.10:  # >10% chance of 50% loss
            suggestions.append(ImprovementSuggestion(
                category='risk',
                priority='high',
                title='High Risk of Ruin',
                description=f'Monte Carlo simulation shows {risk_of_ruin:.1%} probability of losing '
                           '50%+ of capital. This is unacceptably high for most traders.',
                action='Reduce position sizes by 30-50%, implement strict loss limits, '
                       'or add protective filters during high volatility.'
            ))
        
        downside_prob = mc_stats.get('downside_probability', 0)
        if downside_prob > 0.45:  # >45% chance of loss
            suggestions.append(ImprovementSuggestion(
                category='filters',
                priority='medium',
                title='High Downside Probability',
                description=f'{downside_prob:.1%} of Monte Carlo simulations resulted in losses. '
                           'Strategy may not have sufficient edge.',
                action='Add market regime filters, trend confirmation, or seasonal adjustments.'
            ))
    
    # Analyze walk-forward stability
    if wf_stats:
        stability = wf_stats.get('stability_score', 100)
        if stability < 50:
            suggestions.append(ImprovementSuggestion(
                category='stability',
                priority='high',
                title='Unstable Across Time Periods',
                description=f'Walk-forward stability score of {stability:.0f}/100 indicates highly '
                           'variable performance across different time periods. Likely overfitted.',
                action='Simplify strategy logic, use adaptive parameters, or increase lookback periods.'
            ))
        
        degradation = wf_stats.get('degradation_factor', 1.0)
        if degradation < 0.6:  # Test performance < 60% of train
            suggestions.append(ImprovementSuggestion(
                category='stability',
                priority='high',
                title='Severe Out-of-Sample Degradation',
                description=f'Test performance is only {degradation:.1%} of training performance. '
                           'Strong indication of overfitting to historical data.',
                action='Use simpler parameters, add regularization, or employ ensemble methods.'
            ))
    
    # Analyze win rate
    win_rate = metrics.get('win_rate', 0.5)
    if win_rate < 0.40:
        suggestions.append(ImprovementSuggestion(
            category='parameters',
            priority='medium',
            title='Low Win Rate',
            description=f'Win rate of {win_rate:.1%} means strategy loses more often than it wins. '
                       'While acceptable if winners are large, this can be psychologically challenging.',
            action='Consider: (1) Tighter entry criteria, (2) Better timing signals, '
                   '(3) Earlier exits on losing trades.'
        ))
    
    # Analyze volatility
    volatility = metrics.get('volatility', 0)
    if volatility > 0.30:  # >30% annualized
        suggestions.append(ImprovementSuggestion(
            category='risk',
            priority='medium',
            title='High Volatility',
            description=f'Annualized volatility of {volatility:.1%} is elevated. '
                       'High volatility increases drawdown risk and emotional stress.',
            action='Reduce leverage, diversify across strategies, or add volatility targeting.'
        ))
    
    # Analyze return-to-drawdown ratio
    total_return = metrics.get('total_return', 0)
    if max_dd > 0:
        return_dd_ratio = total_return / max_dd
        if return_dd_ratio < 2.0 and total_return > 0:
            suggestions.append(ImprovementSuggestion(
                category='risk',
                priority='low',
                title='Poor Return-to-Drawdown Ratio',
                description=f'Ratio of {return_dd_ratio:.1f}:1 indicates returns are not '
                           'sufficiently compensating for drawdowns experienced.',
                action='Focus on drawdown reduction through better risk management or '
                       'improve returns through signal optimization.'
            ))
    
    # Sort suggestions by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda s: priority_order[s.priority])
    
    return suggestions


def generate_improvement_report(
    suggestions: List[ImprovementSuggestion],
    metrics: Dict[str, float],
    include_details: bool = True
) -> str:
    """
    Generate formatted improvement report.
    
    Args:
        suggestions: List of improvement suggestions
        metrics: Strategy metrics for context
        include_details: Whether to include detailed descriptions
    
    Returns:
        Formatted markdown report
    """
    
    if not suggestions:
        return "✅ **Strategy looks good!** No major improvements suggested at this time.\n"
    
    report = []
    report.append("# 🔍 Strategy Improvement Report\n")
    report.append(f"**Total Suggestions:** {len(suggestions)}\n")
    
    # Count by priority
    high_count = sum(1 for s in suggestions if s.priority == 'high')
    medium_count = sum(1 for s in suggestions if s.priority == 'medium')
    low_count = sum(1 for s in suggestions if s.priority == 'low')
    
    report.append(f"- 🔴 High Priority: {high_count}")
    report.append(f"- 🟡 Medium Priority: {medium_count}")
    report.append(f"- 🟢 Low Priority: {low_count}\n")
    
    report.append("---\n")
    
    # Group by priority
    for priority in ['high', 'medium', 'low']:
        priority_suggestions = [s for s in suggestions if s.priority == priority]
        
        if not priority_suggestions:
            continue
        
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[priority]
        report.append(f"\n## {icon} {priority.upper()} Priority\n")
        
        for i, sug in enumerate(priority_suggestions, 1):
            report.append(f"\n### {i}. {sug.title}\n")
            report.append(f"**Category:** {sug.category.title()}\n")
            
            if include_details:
                report.append(f"\n{sug.description}\n")
            
            report.append(f"\n**✅ Recommended Action:**\n{sug.action}\n")
    
    report.append("\n---\n")
    report.append("💡 **Tip:** Address high-priority items first for maximum impact.\n")
    
    return '\n'.join(report)


def get_quick_tips(metrics: Dict[str, float]) -> List[str]:
    """
    Generate quick, actionable tips based on metrics.
    
    Returns list of 3-5 quick tips for dashboard display.
    """
    tips = []
    
    sharpe = metrics.get('sharpe_ratio', 0)
    max_dd = abs(metrics.get('max_drawdown', 0))
    win_rate = metrics.get('win_rate', 0.5)
    
    if sharpe < 1.0:
        tips.append("💡 Sharpe < 1.0: Consider increasing signal quality over quantity")
    
    if max_dd > 0.20:
        tips.append("⚠️  Drawdown > 20%: Implement tighter risk controls")
    
    if win_rate < 0.45:
        tips.append("🎯 Win rate < 45%: Review entry timing and filters")
    
    if sharpe > 2.0 and max_dd < 0.15:
        tips.append("✨ Excellent risk-adjusted returns! Monitor for consistency")
    
    if not tips:
        tips.append("✅ Strategy metrics look solid - continue monitoring")
    
    return tips[:5]  # Return max 5 tips

