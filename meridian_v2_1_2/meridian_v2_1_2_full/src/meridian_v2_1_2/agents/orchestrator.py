"""
Research Orchestrator

Coordinates multiple AI agents to produce comprehensive research analysis.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from .core import ResearchAgent, AgentInsight


@dataclass
class ResearchReport:
    """Aggregated research report from multiple agents"""
    report_id: str
    strategy_name: str
    agent_insights: Dict[str, Dict[str, Any]]  # agent_name -> analysis results
    all_insights: List[AgentInsight]
    critical_issues: List[AgentInsight]
    recommendations: List[str]
    executive_summary: str
    timestamp: str


class ResearchOrchestrator:
    """
    Orchestrates multiple AI research agents.
    
    Runs all agents in parallel (conceptually) and aggregates
    their insights into a unified research report.
    """
    
    def __init__(self, agents: List[ResearchAgent]):
        """
        Initialize orchestrator with agents.
        
        Args:
            agents: List of ResearchAgent instances
        """
        self.agents = agents
        self.reports_generated = 0
    
    def run_research_cycle(
        self,
        backtest_result: Dict[str, Any],
        selected_agents: Optional[List[str]] = None
    ) -> ResearchReport:
        """
        Run a complete research cycle with all (or selected) agents.
        
        Each agent analyzes the backtest result from their perspective,
        then insights are aggregated into a unified report.
        
        Args:
            backtest_result: Dictionary with metrics, params, mc_stats, etc.
            selected_agents: Optional list of agent names to run (default: all)
        
        Returns:
            ResearchReport: Comprehensive multi-agent analysis
        
        Example:
            >>> orchestrator = ResearchOrchestrator([
            ...     CycleAnalysisAgent(),
            ...     RiskProfilerAgent(),
            ...     BacktestCriticAgent()
            ... ])
            >>> 
            >>> report = orchestrator.run_research_cycle(backtest_result)
            >>> print(report.executive_summary)
            >>> for insight in report.critical_issues:
            ...     print(f"⚠️  {insight.title}")
        """
        
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Filter agents if specified
        if selected_agents:
            active_agents = [a for a in self.agents if a.name in selected_agents]
        else:
            active_agents = self.agents
        
        print(f"🤖 Research Orchestrator: Running {len(active_agents)} agents...")
        
        agent_insights = {}
        all_insights = []
        all_recommendations = []
        critical_issues = []
        
        # Run each agent
        for agent in active_agents:
            print(f"   🔍 {agent.name}...")
            
            try:
                analysis = agent.analyze(backtest_result)
                
                agent_insights[agent.name] = analysis
                
                # Collect insights
                insights = analysis.get('insights', [])
                all_insights.extend(insights)
                
                # Collect recommendations
                recommendations = analysis.get('recommendations', [])
                all_recommendations.extend(recommendations)
                
                # Identify critical issues
                for insight in insights:
                    if insight.priority in ['critical', 'high']:
                        critical_issues.append(insight)
                
            except Exception as e:
                print(f"   ⚠️  {agent.name} failed: {e}")
                agent_insights[agent.name] = {
                    'error': str(e),
                    'insights': [],
                    'recommendations': [],
                    'summary': 'Analysis failed'
                }
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            agent_insights,
            critical_issues,
            backtest_result
        )
        
        self.reports_generated += 1
        
        print(f"✅ Research complete: {len(all_insights)} insights, {len(critical_issues)} critical")
        
        return ResearchReport(
            report_id=report_id,
            strategy_name=backtest_result.get('strategy_name', 'Unknown'),
            agent_insights=agent_insights,
            all_insights=all_insights,
            critical_issues=critical_issues,
            recommendations=list(set(all_recommendations)),  # Deduplicate
            executive_summary=executive_summary,
            timestamp=datetime.now().isoformat()
        )
    
    def get_agent_list(self) -> List[str]:
        """Get list of agent names"""
        return [agent.name for agent in self.agents]
    
    def get_agent_by_name(self, name: str) -> Optional[ResearchAgent]:
        """Get specific agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def _generate_executive_summary(
        self,
        agent_insights: Dict[str, Dict[str, Any]],
        critical_issues: List[AgentInsight],
        backtest_result: Dict[str, Any]
    ) -> str:
        """Generate high-level executive summary"""
        
        metrics = backtest_result.get('metrics', {})
        sharpe = metrics.get('sharpe_ratio', 0)
        total_return = metrics.get('total_return', 0)
        max_dd = abs(metrics.get('max_drawdown', 0))
        
        summary = []
        
        # Overall assessment
        if sharpe > 1.5 and max_dd < 0.15:
            summary.append("🟢 **Overall: STRONG STRATEGY** - Excellent risk-adjusted returns.")
        elif sharpe > 1.0 and max_dd < 0.25:
            summary.append("🟡 **Overall: GOOD STRATEGY** - Solid performance with acceptable risk.")
        elif sharpe > 0.5:
            summary.append("🟡 **Overall: ACCEPTABLE** - Shows promise but needs improvement.")
        else:
            summary.append("🔴 **Overall: WEAK STRATEGY** - Major improvements required.")
        
        # Key metrics
        summary.append(f"\n**Key Metrics:** Sharpe {sharpe:.2f} | Return {total_return:.1%} | DD {max_dd:.1%}")
        
        # Critical issues
        if critical_issues:
            summary.append(f"\n⚠️  **{len(critical_issues)} Critical Issues Identified:**")
            for issue in critical_issues[:3]:  # Show top 3
                summary.append(f"  • {issue.title}")
        else:
            summary.append("\n✅ **No critical issues** detected by agents.")
        
        # Agent consensus
        n_agents = len(agent_insights)
        summary.append(f"\n**Analysis by {n_agents} specialized agents completed.**")
        
        return '\n'.join(summary)
    
    def export_report_to_markdown(self, report: ResearchReport) -> str:
        """Export report as markdown"""
        md = []
        
        md.append(f"# Multi-Agent Research Report\n")
        md.append(f"**Strategy:** {report.strategy_name}")
        md.append(f"**Report ID:** {report.report_id}")
        md.append(f"**Timestamp:** {report.timestamp}\n")
        md.append("---\n")
        
        md.append("## Executive Summary\n")
        md.append(f"{report.executive_summary}\n")
        md.append("---\n")
        
        # Agent-by-agent
        for agent_name, analysis in report.agent_insights.items():
            md.append(f"\n## {agent_name}\n")
            md.append(f"**Summary:** {analysis.get('summary', 'N/A')}\n")
            
            insights = analysis.get('insights', [])
            if insights:
                md.append("\n**Insights:**\n")
                for insight in insights:
                    md.append(f"- [{insight.priority.upper()}] {insight.title}: {insight.content}\n")
            
            recs = analysis.get('recommendations', [])
            if recs:
                md.append("\n**Recommendations:**\n")
                for rec in recs:
                    md.append(f"- {rec}\n")
        
        return '\n'.join(md)


