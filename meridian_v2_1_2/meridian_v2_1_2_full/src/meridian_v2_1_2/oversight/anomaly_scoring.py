"""
Anomaly Scoring for Meridian v2.1.2

Detects unusual behavior across system dimensions.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np


@dataclass
class AnomalyScores:
    """Anomaly scores across system dimensions"""
    strategy_anomaly: float  # 0-1
    execution_anomaly: float
    shadow_anomaly: float
    portfolio_anomaly: float
    overall: float
    details: List[str]


class AnomalyScorer:
    """
    Computes anomaly scores across system dimensions.
    
    Detects:
    - Unusual strategy behavior
    - Abnormal execution patterns
    - Shadow drift anomalies
    - Portfolio behavior changes
    """
    
    def __init__(self, config):
        """
        Initialize anomaly scorer.
        
        Args:
            config: OversightConfig instance
        """
        self.config = config
    
    def score(
        self,
        strategy_data: Dict[str, Any],
        execution_data: Dict[str, Any],
        shadow_data: Dict[str, Any],
        portfolio_data: Dict[str, Any],
        baseline: Dict[str, Any] = None
    ) -> AnomalyScores:
        """
        Compute anomaly scores.
        
        Args:
            strategy_data: Strategy metrics
            execution_data: Execution metrics
            shadow_data: Shadow check results
            portfolio_data: Portfolio state
            baseline: Historical baseline patterns
        
        Returns:
            AnomalyScores
        """
        details = []
        
        # Score strategy anomalies
        strategy_score = self._score_strategy(strategy_data, baseline, details)
        
        # Score execution anomalies
        execution_score = self._score_execution(execution_data, baseline, details)
        
        # Score shadow anomalies
        shadow_score = self._score_shadow(shadow_data, details)
        
        # Score portfolio anomalies
        portfolio_score = self._score_portfolio(portfolio_data, baseline, details)
        
        # Compute overall score
        overall = np.mean([
            strategy_score,
            execution_score,
            shadow_score,
            portfolio_score
        ])
        
        return AnomalyScores(
            strategy_anomaly=strategy_score,
            execution_anomaly=execution_score,
            shadow_anomaly=shadow_score,
            portfolio_anomaly=portfolio_score,
            overall=overall,
            details=details
        )
    
    def _score_strategy(
        self,
        data: Dict[str, Any],
        baseline: Dict[str, Any],
        details: List[str]
    ) -> float:
        """Score strategy behavior anomalies"""
        score = 0.0
        
        # Check signal consistency
        signal_count = data.get('signal_count', 0)
        if baseline and 'avg_signal_count' in baseline:
            expected = baseline['avg_signal_count']
            if expected > 0:
                deviation = abs(signal_count - expected) / expected
                if deviation > 1.0:  # 100% deviation
                    score += 0.3
                    details.append(f"Signal count deviation: {deviation:.1%}")
        
        # Check signal flip-flopping
        if data.get('signal_flips', 0) > 5:
            score += 0.4
            details.append(f"Excessive signal flips: {data['signal_flips']}")
        
        # Check unusual inactivity
        if signal_count == 0 and data.get('days_inactive', 0) > 3:
            score += 0.3
            details.append("Strategy unusually inactive")
        
        return min(score, 1.0)
    
    def _score_execution(
        self,
        data: Dict[str, Any],
        baseline: Dict[str, Any],
        details: List[str]
    ) -> float:
        """Score execution anomalies"""
        score = 0.0
        
        # Check fill rate
        fill_rate = data.get('fill_rate', 1.0)
        if fill_rate < 0.8:  # Less than 80%
            score += 0.4
            details.append(f"Low fill rate: {fill_rate:.1%}")
        
        # Check slippage
        slippage = data.get('avg_slippage', 0.0)
        if baseline and 'avg_slippage' in baseline:
            baseline_slippage = baseline['avg_slippage']
            if slippage > baseline_slippage * 2:  # 2x normal
                score += 0.5
                details.append(f"High slippage: {slippage:.2%} vs {baseline_slippage:.2%}")
        elif slippage > 0.005:  # 0.5% absolute
            score += 0.3
            details.append(f"High slippage: {slippage:.2%}")
        
        # Check execution delays
        if data.get('avg_delay_seconds', 0) > 60:
            score += 0.2
            details.append("Slow execution detected")
        
        return min(score, 1.0)
    
    def _score_shadow(
        self,
        data: Dict[str, Any],
        details: List[str]
    ) -> float:
        """Score shadow/drift anomalies"""
        score = 0.0
        
        # Check drift level
        drift_level = data.get('drift_level', 'none')
        
        if drift_level == 'critical':
            score = 1.0
            details.append("CRITICAL shadow drift detected")
        elif drift_level == 'large':
            score = 0.7
            details.append("Large shadow drift detected")
        elif drift_level == 'small':
            score = 0.3
            details.append("Small shadow drift detected")
        
        # Check drift frequency
        if data.get('drift_events_today', 0) > 3:
            score = max(score, 0.6)
            details.append("Frequent drift events")
        
        return score
    
    def _score_portfolio(
        self,
        data: Dict[str, Any],
        baseline: Dict[str, Any],
        details: List[str]
    ) -> float:
        """Score portfolio behavior anomalies"""
        score = 0.0
        
        # Check exposure jumps
        current_exposure = data.get('total_exposure', 0)
        if baseline and 'avg_exposure' in baseline:
            expected = baseline['avg_exposure']
            if expected > 0:
                jump = abs(current_exposure - expected) / expected
                if jump > 0.5:  # 50% jump
                    score += 0.4
                    details.append(f"Large exposure jump: {jump:.1%}")
        
        # Check turnover
        turnover = data.get('daily_turnover', 0)
        if baseline and 'avg_turnover' in baseline:
            expected = baseline['avg_turnover']
            if expected > 0 and turnover > expected * 3:  # 3x normal
                score += 0.3
                details.append(f"High turnover: {turnover:.0f} vs {expected:.0f}")
        
        # Check concentration
        max_position_pct = data.get('max_position_pct', 0)
        if max_position_pct > 0.5:  # Over 50% in single position
            score += 0.3
            details.append(f"High concentration: {max_position_pct:.1%}")
        
        return min(score, 1.0)


