"""
Specialized AI Research Agent Roles

Seven specialized agents, each with unique expertise and analysis focus.
All rule-based (LLM-ready for future integration).
"""

from typing import Dict, Any, List
from .core import ResearchAgent, AgentInsight
import numpy as np


class CycleAnalysisAgent(ResearchAgent):
    """Specializes in cycle analysis and FLD mechanics"""
    
    def __init__(self):
        super().__init__(
            name="Cycle Analyst",
            description="Expert in market cycles, FLD projections, and cyclical patterns",
            specialization="Cycle Theory & FLD Mechanics"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cycle-related aspects"""
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        metrics = input_data.get('metrics', {})
        
        cycle_length = params.get('cycle_length', params.get('displacement', 20))
        
        # Analyze cycle length
        if cycle_length < 10:
            insights.append(self._create_insight(
                'warning', 'high',
                'Very Short Cycle Length',
                f'Cycle length of {cycle_length} may be too sensitive to noise. '
                'Short cycles capture micro-movements but miss larger trends. '
                'Consider 15-40 range for gold/commodities.',
                {'cycle_length': cycle_length}
            ))
            recommendations.append("Increase cycle_length to 15-25 for better signal quality")
        
        elif cycle_length > 60:
            insights.append(self._create_insight(
                'analysis', 'medium',
                'Long Cycle Configuration',
                f'Cycle length of {cycle_length} focuses on major trends. '
                'Good for reducing whipsaws but may miss intermediate opportunities.',
                {'cycle_length': cycle_length}
            ))
        
        # Analyze displacement vs cycle relationship
        displacement = params.get('displacement', cycle_length // 2)
        if displacement > cycle_length * 0.8:
            insights.append(self._create_insight(
                'discovery', 'medium',
                'High Displacement Ratio',
                f'Displacement ({displacement}) is {displacement/cycle_length:.1%} of cycle length. '
                'This creates leading signals but increases false signals.',
                {'ratio': displacement/cycle_length}
            ))
        
        # Success analysis
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 1.5:
            insights.append(self._create_insight(
                'discovery', 'high',
                'Excellent Cycle Tuning',
                f'Sharpe ratio of {sharpe:.2f} suggests cycle parameters are well-calibrated. '
                'This cycle length effectively captures market rhythm.',
                {'sharpe': sharpe}
            ))
        
        summary = (f"Cycle configuration: {cycle_length} period cycle with {displacement} displacement. "
                  f"{'Well-tuned' if sharpe > 1.0 else 'Needs optimization'}.")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class FLDInspectorAgent(ResearchAgent):
    """Specializes in FLD projection quality and signal timing"""
    
    def __init__(self):
        super().__init__(
            name="FLD Inspector",
            description="Expert in FLD projection quality, signal timing, and lead/lag relationships",
            specialization="FLD Projection Analysis"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze FLD-specific aspects"""
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        metrics = input_data.get('metrics', {})
        
        win_rate = metrics.get('win_rate', 0.5)
        num_trades = metrics.get('num_trades', 0)
        
        # Trade frequency analysis
        if num_trades > 100:
            insights.append(self._create_insight(
                'warning', 'medium',
                'High Trade Frequency',
                f'{num_trades} trades suggests FLD crossovers are frequent. '
                'May indicate overtrading or noise sensitivity.',
                {'num_trades': num_trades}
            ))
            recommendations.append("Add confirmation filters or increase signal threshold")
        
        elif num_trades < 20:
            insights.append(self._create_insight(
                'analysis', 'low',
                'Conservative Trading',
                f'Only {num_trades} trades suggests very selective signals. '
                'Good for quality but may miss opportunities.',
                {'num_trades': num_trades}
            ))
        
        # Win rate analysis
        if win_rate < 0.40:
            insights.append(self._create_insight(
                'warning', 'high',
                'Low FLD Win Rate',
                f'Win rate of {win_rate:.1%} indicates FLD timing needs improvement. '
                'FLD crossovers may be premature or lagging.',
                {'win_rate': win_rate}
            ))
            recommendations.append("Adjust displacement or add trend confirmation")
        
        summary = f"FLD signal quality: {win_rate:.1%} win rate across {num_trades} trades."
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class BacktestCriticAgent(ResearchAgent):
    """Critical review of backtest quality and validity"""
    
    def __init__(self):
        super().__init__(
            name="Backtest Critic",
            description="Evaluates backtest validity, statistical significance, and potential biases",
            specialization="Backtest Quality Assurance"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Critique backtest quality"""
        insights = []
        recommendations = []
        
        metrics = input_data.get('metrics', {})
        
        num_trades = metrics.get('num_trades', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        
        # Sample size analysis
        if num_trades < 30:
            insights.append(self._create_insight(
                'warning', 'critical',
                'Insufficient Sample Size',
                f'Only {num_trades} trades provides low statistical confidence. '
                'Results may not be reliable. Need 30+ trades minimum.',
                {'num_trades': num_trades}
            ))
            recommendations.append("Run longer backtest or reduce signal selectivity")
        
        # Sharpe vs sample size
        if sharpe > 2.5 and num_trades < 50:
            insights.append(self._create_insight(
                'warning', 'high',
                'Suspiciously High Sharpe',
                f'Sharpe of {sharpe:.2f} with only {num_trades} trades may indicate overfitting. '
                'Validate with walk-forward analysis.',
                {'sharpe': sharpe, 'trades': num_trades}
            ))
            recommendations.append("Run walk-forward validation (Phase 5) to verify robustness")
        
        # Data quality check
        if num_trades > 200:
            insights.append(self._create_insight(
                'analysis', 'low',
                'High Sample Size',
                f'{num_trades} trades provides good statistical confidence. '
                'Results are likely more reliable.',
                {'num_trades': num_trades}
            ))
        
        summary = f"Backtest has {num_trades} trades. {'Reliable' if num_trades >= 50 else 'Needs more data'}."
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class RiskProfilerAgent(ResearchAgent):
    """Specializes in risk analysis and tail risk"""
    
    def __init__(self):
        super().__init__(
            name="Risk Profiler",
            description="Analyzes risk metrics, drawdowns, and tail risk scenarios",
            specialization="Risk Management & Tail Risk"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk profile"""
        insights = []
        recommendations = []
        
        metrics = input_data.get('metrics', {})
        mc_stats = input_data.get('mc_stats', {})
        
        max_dd = abs(metrics.get('max_drawdown', 0))
        risk_of_ruin = mc_stats.get('risk_of_ruin', 0) if mc_stats else None
        
        # Drawdown analysis
        if max_dd > 0.30:
            insights.append(self._create_insight(
                'warning', 'critical',
                'Severe Drawdown Risk',
                f'Maximum drawdown of {max_dd:.1%} is catastrophic. '
                'Most traders would have abandoned this strategy.',
                {'max_drawdown': max_dd}
            ))
            recommendations.append("CRITICAL: Reduce position size by 50% minimum")
        
        elif max_dd > 0.20:
            insights.append(self._create_insight(
                'warning', 'high',
                'Elevated Drawdown',
                f'Drawdown of {max_dd:.1%} is concerning. '
                'Acceptable for some but painful for most.',
                {'max_drawdown': max_dd}
            ))
            recommendations.append("Consider reducing leverage or adding protective stops")
        
        # Risk of ruin analysis
        if risk_of_ruin is not None:
            if risk_of_ruin > 0.15:
                insights.append(self._create_insight(
                    'warning', 'critical',
                    'Unacceptable Risk of Ruin',
                    f'{risk_of_ruin:.1%} chance of 50%+ loss per Monte Carlo. '
                    'This is gambling, not trading.',
                    {'risk_of_ruin': risk_of_ruin}
                ))
                recommendations.append("Do NOT trade this strategy without major risk reduction")
        
        # Volatility vs return
        volatility = metrics.get('volatility', 0)
        total_return = metrics.get('total_return', 0)
        
        if volatility > 0 and total_return > 0:
            return_vol_ratio = total_return / volatility
            if return_vol_ratio < 0.5:
                insights.append(self._create_insight(
                    'analysis', 'medium',
                    'Poor Return-to-Volatility Ratio',
                    f'Return/Vol ratio of {return_vol_ratio:.2f} is suboptimal. '
                    'Taking more risk than justified by returns.',
                    {'ratio': return_vol_ratio}
                ))
        
        summary = f"Risk profile: {max_dd:.1%} max DD{',' if risk_of_ruin else '.'} {f'{risk_of_ruin:.1%} risk of ruin' if risk_of_ruin else ''}"
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class ParameterScientistAgent(ResearchAgent):
    """Analyzes parameter choices and suggests optimizations"""
    
    def __init__(self):
        super().__init__(
            name="Parameter Scientist",
            description="Evaluates parameter choices and suggests optimization strategies",
            specialization="Parameter Optimization"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze parameters"""
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        metrics = input_data.get('metrics', {})
        
        # Check if parameters are at boundaries
        param_space = input_data.get('param_space', {})
        
        for param_name, value in params.items():
            if param_name in param_space:
                space_def = param_space[param_name]
                
                if isinstance(space_def, tuple):
                    # Check if at boundaries
                    if value == space_def[0]:
                        insights.append(self._create_insight(
                            'discovery', 'medium',
                            f'Parameter at Lower Bound: {param_name}',
                            f'{param_name} is at minimum value ({value}). '
                            'Consider expanding search space downward.',
                            {param_name: value}
                        ))
                    elif value == space_def[1]:
                        insights.append(self._create_insight(
                            'discovery', 'medium',
                            f'Parameter at Upper Bound: {param_name}',
                            f'{param_name} is at maximum value ({value}). '
                            'Consider expanding search space upward.',
                            {param_name: value}
                        ))
        
        # Suggest evolution/RL if performance is good but could be better
        sharpe = metrics.get('sharpe_ratio', 0)
        if 0.8 < sharpe < 1.5:
            recommendations.append(
                "Run genetic evolution (Phase 6) to find better parameter combination"
            )
        
        if sharpe > 1.0:
            recommendations.append(
                "Use RL training (Phase 7) for fine-tuning around current parameters"
            )
        
        summary = f"Parameters: {len(params)} configured. {'Boundary issues detected' if len(insights) > 0 else 'Within bounds'}."
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class StrategyGeneratorAgent(ResearchAgent):
    """Suggests new strategy variations"""
    
    def __init__(self):
        super().__init__(
            name="Strategy Generator",
            description="Proposes new strategy variants and combinations",
            specialization="Strategy Innovation"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest strategy variations"""
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        metrics = input_data.get('metrics', {})
        
        # Suggest complementary strategies
        if 'cot_threshold' in params:
            recommendations.append(
                "🧬 Combine with TDOM seasonality for multi-factor approach"
            )
        
        if metrics.get('sharpe_ratio', 0) > 1.0:
            recommendations.append(
                "💡 Create ensemble: Blend this with inverse-correlation strategy"
            )
        
        # Suggest filters based on performance
        max_dd = abs(metrics.get('max_drawdown', 0))
        if max_dd > 0.20:
            recommendations.append(
                "🛡️ Add regime filter: Only trade in favorable volatility regimes"
            )
        
        win_rate = metrics.get('win_rate', 0.5)
        if win_rate < 0.45:
            recommendations.append(
                "🎯 Add confirmation layer: Require 2+ indicators to align"
            )
        
        insights.append(self._create_insight(
            'discovery', 'medium',
            'Strategy Variation Opportunities',
            f'Current strategy has {len(recommendations)} potential enhancement paths. '
            'Consider multi-strategy fusion (Phase 5).',
            {'variations': len(recommendations)}
        ))
        
        summary = f"Generated {len(recommendations)} strategy variation suggestions."
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary
        }


class DocumentationAgent(ResearchAgent):
    """Generates strategy documentation"""
    
    def __init__(self):
        super().__init__(
            name="Documentation Agent",
            description="Creates comprehensive strategy documentation and reports",
            specialization="Technical Writing & Documentation"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation"""
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        metrics = input_data.get('metrics', {})
        strategy_name = input_data.get('strategy_name', 'Unknown')
        
        # Generate summary documentation
        doc_sections = []
        
        doc_sections.append(f"## {strategy_name} Strategy\n")
        doc_sections.append(f"**Configuration:** {len(params)} parameters")
        doc_sections.append(f"**Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}")
        doc_sections.append(f"**Total Return:** {metrics.get('total_return', 0):.1%}")
        doc_sections.append(f"**Max Drawdown:** {metrics.get('max_drawdown', 0):.1%}")
        
        documentation = '\n'.join(doc_sections)
        
        insights.append(self._create_insight(
            'analysis', 'low',
            'Documentation Generated',
            'Created structured documentation for strategy.',
            {'doc_length': len(documentation)}
        ))
        
        recommendations.append("Export to notebook for full research report")
        
        summary = "Documentation ready for export."
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary': summary,
            'documentation': documentation
        }


# Additional agents with focused expertise

class COTAnalysisAgent(ResearchAgent):
    """Specializes in COT data analysis"""
    
    def __init__(self):
        super().__init__(
            name="COT Analyst",
            description="Expert in Commitment of Traders data and positioning analysis",
            specialization="COT & Sentiment Analysis"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        insights = []
        recommendations = []
        
        params = input_data.get('params', {})
        
        if 'cot_threshold' in params:
            threshold = params['cot_threshold']
            if threshold < 0.1:
                insights.append(self._create_insight(
                    'analysis', 'medium',
                    'Sensitive COT Filter',
                    f'COT threshold of {threshold:.2f} is very sensitive. Captures many signals.',
                    {'threshold': threshold}
                ))
        
        summary = "COT analysis: Configuration reviewed."
        
        return {'insights': insights, 'recommendations': recommendations, 'summary': summary}


class MarketRegimeAgent(ResearchAgent):
    """Analyzes market regime interactions"""
    
    def __init__(self):
        super().__init__(
            name="Regime Analyst",
            description="Evaluates strategy performance across different market regimes",
            specialization="Market Regime Analysis"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        insights = []
        recommendations = []
        
        metrics = input_data.get('metrics', {})
        
        # Check for regime sensitivity
        volatility = metrics.get('volatility', 0)
        
        if volatility > 0.25:
            insights.append(self._create_insight(
                'analysis', 'medium',
                'High Volatility Exposure',
                'Strategy may be regime-dependent. Test across bull/bear/sideways periods.',
                {'volatility': volatility}
            ))
            recommendations.append("Add volatility regime filter for robustness")
        
        summary = "Regime analysis: Consider regime-adaptive parameters."
        
        return {'insights': insights, 'recommendations': recommendations, 'summary': summary}


class PerformanceAuditorAgent(ResearchAgent):
    """Audits performance metrics for consistency"""
    
    def __init__(self):
        super().__init__(
            name="Performance Auditor",
            description="Validates performance metrics and checks for anomalies",
            specialization="Performance Validation"
        )
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        insights = []
        recommendations = []
        
        metrics = input_data.get('metrics', {})
        
        sharpe = metrics.get('sharpe_ratio', 0)
        total_return = metrics.get('total_return', 0)
        win_rate = metrics.get('win_rate', 0.5)
        
        # Consistency checks
        if sharpe > 2.0 and total_return < 0.20:
            insights.append(self._create_insight(
                'warning', 'medium',
                'Metric Inconsistency',
                f'High Sharpe ({sharpe:.2f}) but moderate return ({total_return:.1%}). '
                'Strategy may be very low volatility.',
                {}
            ))
        
        if win_rate > 0.65 and sharpe < 1.0:
            insights.append(self._create_insight(
                'discovery', 'medium',
                'Small Winner Issue',
                'High win rate but low Sharpe suggests winners are small. Let profits run.',
                {'win_rate': win_rate, 'sharpe': sharpe}
            ))
        
        summary = f"Performance audit: Metrics {'consistent' if len(insights) == 0 else 'show anomalies'}."
        
        return {'insights': insights, 'recommendations': recommendations, 'summary': summary}


