"""
AI Advisor for Meridian v2.1.2

Intelligent advisory system for operators.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AdvisoryMessage:
    """Advisory message from AI"""
    priority: str  # info | warning | urgent
    category: str  # strategy | execution | risk | drift
    message: str
    suggested_action: str


class AIAdvisor:
    """
    AI-powered advisory system.
    
    Provides:
    - Intelligent insights
    - Risk explanations
    - Suggested actions
    - Behavioral analysis
    - Predictive warnings
    """
    
    def __init__(self, config):
        """
        Initialize AI advisor.
        
        Args:
            config: OversightConfig instance
        """
        self.config = config
    
    def generate_advisory(
        self,
        risk_assessment: Any,  # RiskAssessment
        anomaly_scores: Any,  # AnomalyScores
        behavioral_deviations: List[str],
        recent_events: List[Any]
    ) -> List[AdvisoryMessage]:
        """
        Generate advisory messages.
        
        Args:
            risk_assessment: Risk assessment
            anomaly_scores: Anomaly scores
            behavioral_deviations: Behavioral deviations
            recent_events: Recent system events
        
        Returns:
            List of advisory messages
        """
        advisories = []
        
        # Risk-based advisories
        advisories.extend(
            self._generate_risk_advisories(risk_assessment)
        )
        
        # Anomaly-based advisories
        advisories.extend(
            self._generate_anomaly_advisories(anomaly_scores)
        )
        
        # Behavioral advisories
        advisories.extend(
            self._generate_behavioral_advisories(behavioral_deviations)
        )
        
        # Event-based advisories
        advisories.extend(
            self._generate_event_advisories(recent_events)
        )
        
        # Sort by priority
        priority_order = {'urgent': 0, 'warning': 1, 'info': 2}
        advisories.sort(key=lambda a: priority_order.get(a.priority, 3))
        
        return advisories
    
    def _generate_risk_advisories(self, assessment: Any) -> List[AdvisoryMessage]:
        """Generate risk-related advisories"""
        advisories = []
        
        risk_level = getattr(assessment, 'risk_level', None)
        
        if risk_level and str(risk_level) == 'critical':
            advisories.append(AdvisoryMessage(
                priority='urgent',
                category='risk',
                message='CRITICAL RISK LEVEL - System integrity compromised',
                suggested_action='Halt trading immediately and investigate'
            ))
        
        elif risk_level and str(risk_level) == 'high':
            advisories.append(AdvisoryMessage(
                priority='warning',
                category='risk',
                message='High risk level detected across multiple dimensions',
                suggested_action='Reduce exposure by 50% and monitor for 24 hours'
            ))
        
        # Factor-specific advisories
        factors = getattr(assessment, 'contributing_factors', {})
        
        if factors.get('model_risk', 0) > 0.7:
            advisories.append(AdvisoryMessage(
                priority='warning',
                category='risk',
                message='Model risk score elevated - strategy may be unstable',
                suggested_action='Review walk-forward results and consider re-calibration'
            ))
        
        return advisories
    
    def _generate_anomaly_advisories(self, scores: Any) -> List[AdvisoryMessage]:
        """Generate anomaly-related advisories"""
        advisories = []
        
        # Strategy anomalies
        if getattr(scores, 'strategy_anomaly', 0) > 0.7:
            advisories.append(AdvisoryMessage(
                priority='warning',
                category='strategy',
                message='Strategy behavior is abnormal - signals may be unreliable',
                suggested_action='Review signal generation and consider reducing position sizes'
            ))
        
        # Execution anomalies
        if getattr(scores, 'execution_anomaly', 0) > 0.7:
            advisories.append(AdvisoryMessage(
                priority='warning',
                category='execution',
                message='Execution quality degraded - slippage or fill issues',
                suggested_action='Check market liquidity and consider limit orders'
            ))
        
        # Shadow anomalies
        if getattr(scores, 'shadow_anomaly', 0) > 0.7:
            advisories.append(AdvisoryMessage(
                priority='urgent',
                category='drift',
                message='Broker position drift is abnormal',
                suggested_action='Run manual reconciliation and verify all fills'
            ))
        
        return advisories
    
    def _generate_behavioral_advisories(
        self,
        deviations: List[str]
    ) -> List[AdvisoryMessage]:
        """Generate behavioral deviation advisories"""
        advisories = []
        
        if len(deviations) > 3:
            advisories.append(AdvisoryMessage(
                priority='warning',
                category='strategy',
                message=f'Multiple behavioral deviations detected ({len(deviations)})',
                suggested_action='Review system parameters and recent changes'
            ))
        
        return advisories
    
    def _generate_event_advisories(
        self,
        events: List[Any]
    ) -> List[AdvisoryMessage]:
        """Generate event-based advisories"""
        advisories = []
        
        # Count critical events
        critical_count = sum(
            1 for e in events 
            if hasattr(e, 'severity') and e.severity == 'critical'
        )
        
        if critical_count > 0:
            advisories.append(AdvisoryMessage(
                priority='urgent',
                category='risk',
                message=f'{critical_count} critical event(s) detected',
                suggested_action='Review event log and address root causes'
            ))
        
        return advisories
    
    def summarize_day(
        self,
        trades_executed: int,
        pnl: float,
        risk_level: str,
        anomaly_count: int
    ) -> str:
        """
        Generate daily summary.
        
        Args:
            trades_executed: Number of trades
            pnl: Daily PnL
            risk_level: Risk level
            anomaly_count: Number of anomalies
        
        Returns:
            Summary text
        """
        lines = []
        
        lines.append("📊 DAILY OVERSIGHT SUMMARY")
        lines.append(f"   Trades: {trades_executed}")
        lines.append(f"   PnL: ${pnl:,.2f}")
        lines.append(f"   Risk Level: {risk_level.upper()}")
        lines.append(f"   Anomalies: {anomaly_count}")
        
        # Risk commentary
        if risk_level == 'high' or risk_level == 'critical':
            lines.append("\n   ⚠️ ELEVATED RISK - Recommend caution")
        elif risk_level == 'low':
            lines.append("\n   ✓ Normal operations")
        
        return '\n'.join(lines)

