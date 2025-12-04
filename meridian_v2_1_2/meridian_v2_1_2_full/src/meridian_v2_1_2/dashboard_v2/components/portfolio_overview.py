"""
Portfolio Overview Component

Total portfolio metrics and strategy contributions.
"""

from typing import Dict, Any


class PortfolioOverview:
    """
    Portfolio-level overview component.
    
    Displays:
    - Total PnL
    - Total exposure
    - Blended risk
    - Per-strategy contributions
    - Drift/conflict indicators
    """
    
    def __init__(self, api):
        """
        Initialize component.
        
        Args:
            api: MultiStrategyAPI instance
        """
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get portfolio overview data.
        
        Returns:
            Dictionary with all overview metrics
        """
        # Get base portfolio data
        portfolio = self.api.get_portfolio_overview()
        
        # Get risk breakdown
        risk_data = self.api.get_portfolio_risk()
        
        # Get PnL breakdown
        pnl_data = self.api.get_portfolio_pnl()
        
        # Calculate additional metrics
        num_strategies = portfolio['num_strategies']
        avg_risk = portfolio['total_risk'] / num_strategies if num_strategies > 0 else 0.0
        
        # Detect conflicts/drift (simplified for v1)
        has_conflicts = False
        drift_severity = 0.0
        
        for strat in portfolio['strategies']:
            # Check if any strategy has high drift
            if strat.get('health_status') == 'warning':
                has_conflicts = True
                drift_severity = max(drift_severity, 0.5)
            elif strat.get('health_status') == 'error':
                has_conflicts = True
                drift_severity = max(drift_severity, 1.0)
        
        return {
            'total_pnl': portfolio['total_pnl'],
            'total_exposure': portfolio['total_exposure'],
            'total_risk': portfolio['total_risk'],
            'avg_risk_per_strategy': avg_risk,
            'num_strategies': num_strategies,
            'pnl_breakdown': pnl_data['strategies'],
            'risk_breakdown': risk_data['strategies'],
            'has_conflicts': has_conflicts,
            'drift_severity': drift_severity,
            'timestamp': portfolio['timestamp']
        }
    
    def render_summary(self) -> str:
        """Render text summary"""
        data = self.get_data()
        
        lines = [
            "📊 PORTFOLIO OVERVIEW",
            "=" * 50,
            f"Total PnL: ${data['total_pnl']:,.2f}",
            f"Total Exposure: ${data['total_exposure']:,.2f}",
            f"Total Risk: {data['total_risk']:.2f}",
            f"Strategies: {data['num_strategies']}",
            ""
        ]
        
        if data['has_conflicts']:
            lines.append(f"⚠️ Conflicts Detected (Severity: {data['drift_severity']:.1%})")
        else:
            lines.append("✅ No Conflicts")
        
        lines.append("")
        lines.append("Strategy Contributions:")
        for strat in data['pnl_breakdown']:
            lines.append(f"  {strat['name']}: ${strat['pnl']:,.2f} ({strat['contribution_pct']:.1f}%)")
        
        return "\n".join(lines)


