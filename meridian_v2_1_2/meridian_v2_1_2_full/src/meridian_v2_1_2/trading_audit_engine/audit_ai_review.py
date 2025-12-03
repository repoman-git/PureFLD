"""
Multi-AI Trade Reviewer

Multiple AI models review and vote on trading decisions.
Provides consensus-based trade validation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class AIVerdict(Enum):
    """AI verdict on trade"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEUTRAL = "NEUTRAL"


@dataclass
class AITradeVerdict:
    """Verdict from a single AI model"""
    model_name: str
    verdict: AIVerdict
    confidence: float  # 0-1
    reasoning: str
    concerns: List[str]
    advantages: List[str]


class MultiAITradeReviewer:
    """
    Multi-AI trade review system.
    
    Multiple AI models (Claude, Gemini, Grok, ChatGPT) review each trade
    and provide consensus-based validation.
    """
    
    def __init__(self, enabled_models: Optional[List[str]] = None):
        """
        Initialize multi-AI reviewer.
        
        Args:
            enabled_models: List of AI models to use
        """
        self.enabled_models = enabled_models or ['claude', 'gemini', 'grok', 'chatgpt']
    
    def review_trade(
        self,
        trade: Dict[str, Any],
        strategy_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get multi-AI review of proposed trade.
        
        Args:
            trade: Trade intent
            strategy_context: Strategy rules and historical performance
        
        Returns:
            Dictionary with:
                - verdicts: List of AITradeVerdict from each model
                - consensus: Overall consensus verdict
                - confidence: Consensus confidence (0-100)
                - should_execute: Boolean recommendation
        """
        
        verdicts = []
        
        # Get verdict from each enabled AI model (mock for now)
        for model in self.enabled_models:
            verdict = self._get_model_verdict(model, trade, strategy_context)
            verdicts.append(verdict)
        
        # Calculate consensus
        consensus, confidence = self._calculate_consensus(verdicts)
        
        # Final recommendation
        should_execute = consensus == AIVerdict.APPROVE and confidence > 60
        
        return {
            'verdicts': verdicts,
            'consensus': consensus.value,
            'confidence': confidence,
            'should_execute': should_execute,
            'num_models': len(verdicts)
        }
    
    def _get_model_verdict(
        self,
        model_name: str,
        trade: Dict[str, Any],
        context: Dict[str, Any]
    ) -> AITradeVerdict:
        """
        Get verdict from specific AI model (mock implementation).
        
        In Phase 11, this will make actual LLM API calls.
        For now, uses rule-based logic.
        """
        
        # Rule-based mock verdict
        signal_strength = trade.get('signal_strength', 0)
        risk_reward = trade.get('reward_risk_ratio', 1.0)
        
        # Simple scoring
        score = signal_strength * 50 + (risk_reward / 3.0) * 50
        
        if score > 70:
            verdict = AIVerdict.APPROVE
            reasoning = f"{model_name}: Strong signal with good risk/reward"
            advantages = ["Good signal strength", "Acceptable R:R ratio"]
            concerns = []
        elif score > 40:
            verdict = AIVerdict.NEUTRAL
            reasoning = f"{model_name}: Marginal trade quality"
            advantages = []
            concerns = ["Moderate signal strength", "Consider better setup"]
        else:
            verdict = AIVerdict.REJECT
            reasoning = f"{model_name}: Weak trade setup"
            advantages = []
            concerns = ["Low signal quality", "Poor risk/reward"]
        
        confidence = min(1.0, score / 100)
        
        return AITradeVerdict(
            model_name=model_name,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            concerns=concerns,
            advantages=advantages
        )
    
    def _calculate_consensus(
        self,
        verdicts: List[AITradeVerdict]
    ) -> tuple[AIVerdict, float]:
        """Calculate consensus from multiple AI verdicts"""
        
        if not verdicts:
            return AIVerdict.NEUTRAL, 0
        
        # Count votes
        approve_count = sum(1 for v in verdicts if v.verdict == AIVerdict.APPROVE)
        reject_count = sum(1 for v in verdicts if v.verdict == AIVerdict.REJECT)
        
        total = len(verdicts)
        
        # Consensus verdict
        if approve_count > total / 2:
            consensus = AIVerdict.APPROVE
        elif reject_count > total / 2:
            consensus = AIVerdict.REJECT
        else:
            consensus = AIVerdict.NEUTRAL
        
        # Confidence based on agreement level
        max_count = max(approve_count, reject_count, total - approve_count - reject_count)
        confidence = (max_count / total) * 100
        
        # Average individual confidences
        avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts) * 100
        
        # Combined confidence
        final_confidence = (confidence + avg_confidence) / 2
        
        return consensus, final_confidence

