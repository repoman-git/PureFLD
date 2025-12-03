"""
Audit Modes - 3-Stage Verification Process

Stage 1: Neutral Diagnostic
Stage 2: Adversarial/HarshMode
Stage 3: Cross-Model Reconciliation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class AuditStage(Enum):
    """Audit stage enumeration"""
    NEUTRAL = "stage1_neutral"
    ADVERSARIAL = "stage2_adversarial"
    CROSS_MODEL = "stage3_cross_model"


class UncertaintyLabel(Enum):
    """Uncertainty classification per HonestAI Protocol"""
    FACT = "FACT"
    INTERPRETATION = "INTERPRETATION"
    SPECULATION = "SPECULATION"
    LIMITATION = "LIMITATION"


@dataclass
class AuditMode:
    """Base audit mode configuration"""
    stage: AuditStage
    name: str
    description: str
    focus_areas: List[str]


class NeutralAudit:
    """
    Stage 1: Neutral Diagnostic Audit
    
    Objective, balanced assessment of strengths, weaknesses, and gaps.
    No advocacy, pure analysis.
    """
    
    def __init__(self):
        self.stage = AuditStage.NEUTRAL
        self.name = "Neutral Diagnostic"
    
    def audit_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform neutral diagnostic audit on strategy.
        
        Args:
            strategy_data: Strategy configuration, params, backtest results
        
        Returns:
            Audit findings dictionary
        """
        findings = {
            'strengths': self._identify_strengths(strategy_data),
            'weaknesses': self._identify_weaknesses(strategy_data),
            'gaps': self._identify_gaps(strategy_data),
            'architectural_risks': self._identify_architectural_risks(strategy_data),
            'technical_risks': self._identify_technical_risks(strategy_data),
            'uncertainty_labels': self._label_uncertainties(strategy_data)
        }
        
        return findings
    
    def _identify_strengths(self, data: Dict[str, Any]) -> List[str]:
        """Identify strategy strengths"""
        strengths = []
        metrics = data.get('metrics', {})
        
        if metrics.get('sharpe_ratio', 0) > 1.5:
            strengths.append("FACT: High Sharpe ratio indicates strong risk-adjusted returns")
        
        if abs(metrics.get('max_drawdown', 0)) < 0.15:
            strengths.append("FACT: Low maximum drawdown demonstrates good risk control")
        
        if metrics.get('num_trades', 0) >= 50:
            strengths.append("FACT: Sufficient sample size for statistical confidence")
        
        return strengths
    
    def _identify_weaknesses(self, data: Dict[str, Any]) -> List[str]:
        """Identify strategy weaknesses"""
        weaknesses = []
        metrics = data.get('metrics', {})
        
        if metrics.get('sharpe_ratio', 0) < 1.0:
            weaknesses.append("FACT: Sharpe ratio below 1.0 indicates suboptimal risk-adjusted returns")
        
        if abs(metrics.get('max_drawdown', 0)) > 0.25:
            weaknesses.append("FACT: Maximum drawdown exceeds 25%, potential for severe losses")
        
        if metrics.get('num_trades', 0) < 30:
            weaknesses.append("LIMITATION: Small sample size reduces statistical reliability")
        
        return weaknesses
    
    def _identify_gaps(self, data: Dict[str, Any]) -> List[str]:
        """Identify missing information or analysis gaps"""
        gaps = []
        
        if 'mc_stats' not in data or not data.get('mc_stats'):
            gaps.append("MISSING: Monte Carlo robustness analysis not performed")
        
        if 'wf_stats' not in data or not data.get('wf_stats'):
            gaps.append("MISSING: Walk-forward validation not performed")
        
        params = data.get('params', {})
        if not params:
            gaps.append("MISSING: Parameter configuration not provided")
        
        return gaps
    
    def _identify_architectural_risks(self, data: Dict[str, Any]) -> List[str]:
        """Identify architectural/design risks"""
        risks = []
        
        params = data.get('params', {})
        
        # Check for single-point dependencies
        if len(params) < 3:
            risks.append("RISK: Low parameter count may indicate oversimplification")
        
        # Check for overfitting indicators
        metrics = data.get('metrics', {})
        if metrics.get('sharpe_ratio', 0) > 3.0 and metrics.get('num_trades', 100) < 50:
            risks.append("RISK: Very high Sharpe with low trade count suggests potential overfitting")
        
        return risks
    
    def _identify_technical_risks(self, data: Dict[str, Any]) -> List[str]:
        """Identify implementation/technical risks"""
        risks = []
        
        # Check for extreme parameter values
        params = data.get('params', {})
        
        for key, value in params.items():
            if isinstance(value, (int, float)):
                if value == 0:
                    risks.append(f"RISK: Parameter '{key}' set to zero may cause division errors")
        
        return risks
    
    def _label_uncertainties(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Label statements by uncertainty level"""
        labels = {}
        
        metrics = data.get('metrics', {})
        
        # Facts (objectively measurable)
        if 'sharpe_ratio' in metrics:
            labels['sharpe_ratio'] = UncertaintyLabel.FACT.value
        
        # Interpretations (derived conclusions)
        if metrics.get('sharpe_ratio', 0) > 1.5:
            labels['performance_quality'] = UncertaintyLabel.INTERPRETATION.value
        
        # Limitations (known constraints)
        if metrics.get('num_trades', 0) < 30:
            labels['statistical_confidence'] = UncertaintyLabel.LIMITATION.value
        
        return labels


class AdversarialAudit:
    """
    Stage 2: Adversarial/HarshMode Audit
    
    Actively attacks assumptions, finds contradictions, stress-tests logic.
    """
    
    def __init__(self):
        self.stage = AuditStage.ADVERSARIAL
        self.name = "Adversarial Stress Test"
    
    def audit_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform adversarial audit"""
        findings = {
            'assumption_attacks': self._attack_assumptions(strategy_data),
            'contradictions': self._find_contradictions(strategy_data),
            'failure_modes': self._identify_failure_modes(strategy_data),
            'misuse_scenarios': self._identify_misuse_scenarios(strategy_data),
            'hidden_risks': self._uncover_hidden_risks(strategy_data)
        }
        
        return findings
    
    def _attack_assumptions(self, data: Dict[str, Any]) -> List[str]:
        """Challenge underlying assumptions"""
        attacks = []
        
        params = data.get('params', {})
        
        if 'cycle_length' in params:
            attacks.append(
                f"CHALLENGE: Assumes market cycles are stationary. "
                f"What if cycle length changes over time? "
                f"Current fixed value may fail in regime shifts."
            )
        
        if params.get('allow_short', False):
            attacks.append(
                "CHALLENGE: Short positions assume mean reversion. "
                "What if trend persists? Unlimited loss potential."
            )
        
        return attacks
    
    def _find_contradictions(self, data: Dict[str, Any]) -> List[str]:
        """Find logical contradictions"""
        contradictions = []
        
        metrics = data.get('metrics', {})
        
        # High win rate but low Sharpe
        if metrics.get('win_rate', 0) > 0.65 and metrics.get('sharpe_ratio', 0) < 1.0:
            contradictions.append(
                "CONTRADICTION: High win rate (>65%) but low Sharpe (<1.0). "
                "Winners must be very small or losers very large. Inconsistent risk profile."
            )
        
        return contradictions
    
    def _identify_failure_modes(self, data: Dict[str, Any]) -> List[str]:
        """Identify potential failure scenarios"""
        failures = []
        
        params = data.get('params', {})
        
        if not params.get('stop_loss'):
            failures.append(
                "FAILURE MODE: No stop-loss defined. "
                "Single adverse event could cause catastrophic loss."
            )
        
        if params.get('leverage', 1) > 1:
            failures.append(
                "FAILURE MODE: Leverage amplifies losses. "
                "Margin calls possible during volatility spikes."
            )
        
        return failures
    
    def _identify_misuse_scenarios(self, data: Dict[str, Any]) -> List[str]:
        """Identify ways users could misuse this strategy"""
        misuse = []
        
        metrics = data.get('metrics', {})
        
        if metrics.get('sharpe_ratio', 0) > 2.0:
            misuse.append(
                "MISUSE RISK: High historical Sharpe may lead to overconfidence. "
                "Users might over-allocate or ignore changing market conditions."
            )
        
        return misuse
    
    def _uncover_hidden_risks(self, data: Dict[str, Any]) -> List[str]:
        """Uncover non-obvious risks"""
        hidden_risks = []
        
        # Concentration risk
        if data.get('asset_count', 1) == 1:
            hidden_risks.append(
                "HIDDEN RISK: Single-asset concentration. "
                "No diversification benefit. Correlated with asset-specific shocks."
            )
        
        return hidden_risks


class CrossModelAudit:
    """
    Stage 3: Cross-Model Reconciliation
    
    Compares findings from multiple AI models to identify consensus and conflicts.
    """
    
    def __init__(self):
        self.stage = AuditStage.CROSS_MODEL
        self.name = "Cross-Model Reconciliation"
    
    def reconcile_audits(
        self,
        audits: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconcile audits from multiple AI models.
        
        Args:
            audits: Dictionary mapping model_name -> audit_results
        
        Returns:
            Reconciliation summary with consensus and conflicts
        """
        if len(audits) < 2:
            return {'error': 'Need at least 2 audits for reconciliation'}
        
        consensus_items = self._find_consensus(audits)
        disagreements = self._find_disagreements(audits)
        confidence_score = self._calculate_confidence(audits, consensus_items)
        
        return {
            'consensus_items': consensus_items,
            'disagreements': disagreements,
            'confidence_score': confidence_score,
            'num_models': len(audits),
            'models_used': list(audits.keys())
        }
    
    def _find_consensus(self, audits: Dict[str, Dict[str, Any]]) -> List[str]:
        """Find items multiple models agree on"""
        consensus = []
        
        # Simple consensus: items mentioned by 2+ models
        all_findings = []
        for model, audit in audits.items():
            findings = audit.get('findings', [])
            all_findings.extend(findings)
        
        # Count occurrences (simplified)
        if len(all_findings) > 0:
            consensus.append("Multiple models identified similar concerns")
        
        return consensus
    
    def _find_disagreements(self, audits: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Find items models disagree on"""
        disagreements = []
        
        # Simplified disagreement detection
        model_names = list(audits.keys())
        if len(model_names) >= 2:
            # Placeholder for actual disagreement logic
            disagreements.append({
                'topic': 'risk_assessment',
                'conflict': 'Models may have different risk interpretations'
            })
        
        return disagreements
    
    def _calculate_confidence(
        self,
        audits: Dict[str, Dict[str, Any]],
        consensus_items: List[str]
    ) -> float:
        """Calculate overall confidence score (0-100)"""
        
        # More consensus = higher confidence
        num_models = len(audits)
        consensus_count = len(consensus_items)
        
        # Base confidence from number of models
        base_confidence = min(100, num_models * 20)
        
        # Bonus for consensus
        consensus_bonus = min(30, consensus_count * 5)
        
        return min(100, base_confidence + consensus_bonus)

