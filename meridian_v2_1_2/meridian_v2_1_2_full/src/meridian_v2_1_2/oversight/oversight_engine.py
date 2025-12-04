"""
Oversight Engine for Meridian v2.1.2

Main AI monitoring and supervision loop.
"""

from typing import Dict, Any
from datetime import datetime

from .oversight_config import OversightConfig
from .anomaly_scoring import AnomalyScorer
from .behavioural_patterns import BehavioralPatterns
from .risk_reasoner import RiskReasoner
from .ai_advisor import AIAdvisor
from .oversight_reporter import generate_oversight_report


class OversightEngine:
    """
    Main oversight and monitoring engine.
    
    Continuously monitors system health and provides
    intelligent supervision.
    """
    
    def __init__(self, config: OversightConfig):
        """
        Initialize oversight engine.
        
        Args:
            config: Oversight configuration
        """
        self.config = config
        
        # Initialize components
        self.anomaly_scorer = AnomalyScorer(config)
        self.behavioral = BehavioralPatterns(config)
        self.risk_reasoner = RiskReasoner(config)
        self.advisor = AIAdvisor(config)
        
        self.last_check = None
        self.check_history = []
    
    def run_oversight_check(
        self,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run complete oversight check.
        
        Args:
            system_state: Current system state dict containing:
                - strategy_data
                - execution_data
                - shadow_data
                - portfolio_data
                - model_risk_score (optional)
                - recent_events (optional)
        
        Returns:
            Dict with oversight results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'enabled': self.config.enabled,
            'success': False
        }
        
        if not self.config.enabled:
            results['message'] = 'Oversight disabled'
            return results
        
        try:
            # Extract data
            strategy_data = system_state.get('strategy_data', {})
            execution_data = system_state.get('execution_data', {})
            shadow_data = system_state.get('shadow_data', {})
            portfolio_data = system_state.get('portfolio_data', {})
            model_risk_score = system_state.get('model_risk_score', 0.0)
            recent_events = system_state.get('recent_events', [])
            
            # Update behavioral baseline
            observation = {
                'signal_count': strategy_data.get('signal_count', 0),
                'total_exposure': portfolio_data.get('total_exposure', 0),
                'daily_turnover': portfolio_data.get('daily_turnover', 0),
                'avg_slippage': execution_data.get('avg_slippage', 0),
                'fill_rate': execution_data.get('fill_rate', 1.0),
                'drift_events': shadow_data.get('drift_events_today', 0)
            }
            self.behavioral.update(observation)
            
            # Compute baseline
            baseline = self.behavioral.compute_baseline()
            baseline_dict = {
                'avg_signal_count': baseline.avg_signal_count,
                'avg_exposure': baseline.avg_exposure,
                'avg_turnover': baseline.avg_turnover,
                'avg_slippage': baseline.avg_slippage
            }
            
            # Compute anomaly scores
            anomaly_scores = self.anomaly_scorer.score(
                strategy_data=strategy_data,
                execution_data=execution_data,
                shadow_data=shadow_data,
                portfolio_data=portfolio_data,
                baseline=baseline_dict
            )
            
            # Detect behavioral deviations
            behavioral_deviations = self.behavioral.detect_deviations(observation)
            
            # Assess risk
            risk_assessment = self.risk_reasoner.assess(
                anomaly_scores=anomaly_scores,
                model_risk_score=model_risk_score,
                shadow_drift_level=shadow_data.get('drift_level', 'none'),
                execution_quality=execution_data.get('avg_slippage', 0),
                behavioral_deviations=behavioral_deviations
            )
            
            # Generate advisories
            advisories = self.advisor.generate_advisory(
                risk_assessment=risk_assessment,
                anomaly_scores=anomaly_scores,
                behavioral_deviations=behavioral_deviations,
                recent_events=recent_events
            )
            
            # Build results
            results.update({
                'success': True,
                'anomaly_scores': {
                    'strategy': anomaly_scores.strategy_anomaly,
                    'execution': anomaly_scores.execution_anomaly,
                    'shadow': anomaly_scores.shadow_anomaly,
                    'portfolio': anomaly_scores.portfolio_anomaly,
                    'overall': anomaly_scores.overall
                },
                'risk_assessment': {
                    'level': risk_assessment.risk_level.value,
                    'score': risk_assessment.risk_score,
                    'should_halt': risk_assessment.should_halt,
                    'recommendations': risk_assessment.recommendations
                },
                'advisories': [
                    {
                        'priority': a.priority,
                        'category': a.category,
                        'message': a.message,
                        'action': a.suggested_action
                    }
                    for a in advisories
                ],
                'behavioral_deviations': behavioral_deviations
            })
            
            # Generate report if enabled
            if self.config.write_reports:
                generate_oversight_report(results, self.config)
            
            # Store in history
            self.check_history.append(results)
            self.last_check = datetime.now()
            
        except Exception as e:
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def should_alert_operator(self, results: Dict[str, Any]) -> bool:
        """
        Determine if operator should be alerted.
        
        Args:
            results: Oversight check results
        
        Returns:
            True if alert needed
        """
        if not results.get('success'):
            return True
        
        # Check anomaly threshold
        anomaly_overall = results.get('anomaly_scores', {}).get('overall', 0)
        if anomaly_overall > self.config.anomaly_alert_threshold:
            return True
        
        # Check risk threshold
        risk_score = results.get('risk_assessment', {}).get('score', 0)
        if risk_score > self.config.risk_alert_threshold:
            return True
        
        # Check for urgent advisories
        advisories = results.get('advisories', [])
        if any(a['priority'] == 'urgent' for a in advisories):
            return True
        
        return False


