"""
Risk Reasoner for Meridian v2.1.2

AI-based risk assessment using multiple signals.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class RiskLevel(str, Enum):
    """Overall risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskAssessment:
    """Complete risk assessment"""
    risk_level: RiskLevel
    risk_score: float  # 0-1
    contributing_factors: Dict[str, float]
    recommendations: list
    should_halt: bool


class RiskReasoner:
    """
    AI-based risk assessment engine.
    
    Integrates:
    - Anomaly scores
    - Model risk
    - Shadow drift
    - Behavioral deviations
    - Execution quality
    """
    
    def __init__(self, config):
        """
        Initialize risk reasoner.
        
        Args:
            config: OversightConfig instance
        """
        self.config = config
        
        # Weights for risk components
        self.weights = {
            'anomalies': 0.30,
            'model_risk': 0.25,
            'shadow_drift': 0.25,
            'execution_quality': 0.10,
            'behavioral_deviation': 0.10
        }
    
    def assess(
        self,
        anomaly_scores: Any,  # AnomalyScores
        model_risk_score: float,
        shadow_drift_level: str,
        execution_quality: float,
        behavioral_deviations: list
    ) -> RiskAssessment:
        """
        Perform complete risk assessment.
        
        Args:
            anomaly_scores: Anomaly scores
            model_risk_score: Model risk score (0-1)
            shadow_drift_level: Shadow drift level
            execution_quality: Execution quality score (0-1, lower is better)
            behavioral_deviations: List of deviations
        
        Returns:
            RiskAssessment
        """
        contributing_factors = {}
        recommendations = []
        
        # Factor 1: Anomalies
        anomaly_contrib = getattr(anomaly_scores, 'overall', 0.0)
        contributing_factors['anomalies'] = anomaly_contrib
        
        # Factor 2: Model risk
        contributing_factors['model_risk'] = model_risk_score
        
        # Factor 3: Shadow drift
        drift_score = self._drift_level_to_score(shadow_drift_level)
        contributing_factors['shadow_drift'] = drift_score
        
        # Factor 4: Execution quality
        contributing_factors['execution_quality'] = execution_quality
        
        # Factor 5: Behavioral deviations
        deviation_score = min(len(behavioral_deviations) * 0.2, 1.0)
        contributing_factors['behavioral_deviation'] = deviation_score
        
        # Compute weighted risk score
        risk_score = sum(
            self.weights[k] * v 
            for k, v in contributing_factors.items()
            if k in self.weights
        )
        
        # Classify risk level
        risk_level = self._classify_risk(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level,
            contributing_factors,
            anomaly_scores
        )
        
        # Determine if should halt
        should_halt = (
            risk_level == RiskLevel.CRITICAL or
            drift_score >= 1.0 or
            anomaly_contrib > 0.9
        )
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            should_halt=should_halt
        )
    
    def _drift_level_to_score(self, drift_level: str) -> float:
        """Convert drift level to numeric score"""
        mapping = {
            'none': 0.0,
            'small': 0.3,
            'large': 0.7,
            'critical': 1.0
        }
        return mapping.get(drift_level, 0.5)
    
    def _classify_risk(self, risk_score: float) -> RiskLevel:
        """Classify risk level from score"""
        if risk_score < 0.35:
            return RiskLevel.LOW
        elif risk_score < 0.65:
            return RiskLevel.MEDIUM
        elif risk_score < 0.85:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        factors: Dict[str, float],
        anomaly_scores: Any
    ) -> list:
        """Generate recommendations based on risk factors"""
        recommendations = []
        
        # High anomaly recommendations
        if factors.get('anomalies', 0) > 0.7:
            recommendations.append(
                "High anomaly scores detected - review strategy signals"
            )
        
        # Model risk recommendations
        if factors.get('model_risk', 0) > 0.6:
            recommendations.append(
                "Elevated model risk - consider reducing position sizes"
            )
        
        # Shadow drift recommendations
        if factors.get('shadow_drift', 0) > 0.5:
            recommendations.append(
                "Shadow drift detected - reconcile positions immediately"
            )
        
        # Execution quality recommendations
        if factors.get('execution_quality', 0) > 0.5:
            recommendations.append(
                "Poor execution quality - check slippage and fill rates"
            )
        
        # Critical risk recommendations
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append(
                "⚠️ CRITICAL RISK - Consider halting trading until resolved"
            )
        elif risk_level == RiskLevel.HIGH:
            recommendations.append(
                "High risk - Reduce exposure and monitor closely"
            )
        
        return recommendations


