"""
Audit Orchestrator

Coordinates multi-stage, multi-model audit process.
Routes requests, validates responses, aggregates findings.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from .audit_modes import NeutralAudit, AdversarialAudit, CrossModelAudit, AuditStage
from .model_profiles import get_model_profile


@dataclass
class AuditResult:
    """Complete audit result"""
    audit_id: str
    strategy_name: str
    model_used: str
    stage: str
    findings: Dict[str, Any]
    confidence_score: float
    timestamp: str
    summary: str
    risk_flags: List[str]


class AuditOrchestrator:
    """
    Orchestrates multi-stage audit process.
    
    Handles routing to correct AI models, validating responses,
    and aggregating findings.
    """
    
    def __init__(self, default_model: str = 'claude'):
        """
        Initialize audit orchestrator.
        
        Args:
            default_model: Default AI model to use
        """
        self.default_model = default_model
        self.audits_performed = 0
        
        # Initialize audit modes
        self.neutral_auditor = NeutralAudit()
        self.adversarial_auditor = AdversarialAudit()
        self.cross_model_auditor = CrossModelAudit()
    
    def run_full_audit(
        self,
        strategy_data: Dict[str, Any],
        model: Optional[str] = None,
        stages: Optional[List[str]] = None
    ) -> Dict[str, AuditResult]:
        """
        Run complete multi-stage audit.
        
        Args:
            strategy_data: Strategy configuration and results
            model: AI model to use (default: self.default_model)
            stages: Which stages to run (default: all)
        
        Returns:
            Dictionary mapping stage -> AuditResult
        """
        if model is None:
            model = self.default_model
        
        if stages is None:
            stages = ['neutral', 'adversarial']
        
        results = {}
        
        # Stage 1: Neutral
        if 'neutral' in stages:
            neutral_result = self._run_neutral_audit(strategy_data, model)
            results['neutral'] = neutral_result
        
        # Stage 2: Adversarial
        if 'adversarial' in stages:
            adversarial_result = self._run_adversarial_audit(strategy_data, model)
            results['adversarial'] = adversarial_result
        
        # Stage 3: Cross-model (if multiple models)
        if 'cross_model' in stages and len(results) > 1:
            cross_result = self._run_cross_model_audit(results)
            results['cross_model'] = cross_result
        
        self.audits_performed += 1
        
        return results
    
    def quick_audit(
        self,
        strategy_data: Dict[str, Any],
        model: Optional[str] = None
    ) -> AuditResult:
        """
        Quick audit (Stage 1 only).
        
        Args:
            strategy_data: Strategy data
            model: AI model to use
        
        Returns:
            Single AuditResult
        """
        return self._run_neutral_audit(strategy_data, model or self.default_model)
    
    def _run_neutral_audit(
        self,
        strategy_data: Dict[str, Any],
        model: str
    ) -> AuditResult:
        """Run Stage 1: Neutral audit"""
        
        profile = get_model_profile(model)
        
        findings = self.neutral_auditor.audit_strategy(strategy_data)
        
        # Calculate confidence
        confidence = self._calculate_stage1_confidence(findings)
        
        # Extract risk flags
        risk_flags = findings.get('technical_risks', []) + findings.get('architectural_risks', [])
        
        # Generate summary
        summary = self._generate_neutral_summary(findings)
        
        audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return AuditResult(
            audit_id=audit_id,
            strategy_name=strategy_data.get('strategy_name', 'Unknown'),
            model_used=model,
            stage='neutral',
            findings=findings,
            confidence_score=confidence,
            timestamp=datetime.now().isoformat(),
            summary=summary,
            risk_flags=risk_flags
        )
    
    def _run_adversarial_audit(
        self,
        strategy_data: Dict[str, Any],
        model: str
    ) -> AuditResult:
        """Run Stage 2: Adversarial audit"""
        
        findings = self.adversarial_auditor.audit_strategy(strategy_data)
        
        # Calculate confidence (lower in adversarial mode)
        confidence = self._calculate_stage2_confidence(findings)
        
        # Extract all risk items
        risk_flags = (
            findings.get('assumption_attacks', []) +
            findings.get('failure_modes', []) +
            findings.get('hidden_risks', [])
        )
        
        # Generate summary
        summary = self._generate_adversarial_summary(findings)
        
        audit_id = f"audit_adv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return AuditResult(
            audit_id=audit_id,
            strategy_name=strategy_data.get('strategy_name', 'Unknown'),
            model_used=model,
            stage='adversarial',
            findings=findings,
            confidence_score=confidence,
            timestamp=datetime.now().isoformat(),
            summary=summary,
            risk_flags=risk_flags
        )
    
    def _run_cross_model_audit(
        self,
        previous_audits: Dict[str, AuditResult]
    ) -> AuditResult:
        """Run Stage 3: Cross-model reconciliation"""
        
        # Convert to format expected by cross-model auditor
        audits_dict = {}
        for stage, result in previous_audits.items():
            audits_dict[result.model_used] = result.findings
        
        reconciliation = self.cross_model_auditor.reconcile_audits(audits_dict)
        
        audit_id = f"audit_cross_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return AuditResult(
            audit_id=audit_id,
            strategy_name=previous_audits['neutral'].strategy_name,
            model_used='cross_model',
            stage='cross_model',
            findings=reconciliation,
            confidence_score=reconciliation.get('confidence_score', 50),
            timestamp=datetime.now().isoformat(),
            summary=f"Cross-model analysis: {len(audits_dict)} models compared",
            risk_flags=[]
        )
    
    def _calculate_stage1_confidence(self, findings: Dict[str, Any]) -> float:
        """Calculate confidence for neutral audit"""
        strengths = len(findings.get('strengths', []))
        weaknesses = len(findings.get('weaknesses', []))
        gaps = len(findings.get('gaps', []))
        
        # More strengths, fewer gaps = higher confidence
        base = 50
        base += strengths * 5
        base -= gaps * 10
        base -= weaknesses * 3
        
        return max(0, min(100, base))
    
    def _calculate_stage2_confidence(self, findings: Dict[str, Any]) -> float:
        """Calculate confidence for adversarial audit"""
        attacks = len(findings.get('assumption_attacks', []))
        failures = len(findings.get('failure_modes', []))
        
        # More issues found = lower confidence in strategy
        confidence = 100 - (attacks * 10) - (failures * 15)
        
        return max(0, min(100, confidence))
    
    def _generate_neutral_summary(self, findings: Dict[str, Any]) -> str:
        """Generate summary for neutral audit"""
        strengths = len(findings.get('strengths', []))
        weaknesses = len(findings.get('weaknesses', []))
        gaps = len(findings.get('gaps', []))
        
        return (
            f"Neutral audit complete: {strengths} strengths, {weaknesses} weaknesses, "
            f"{gaps} gaps identified."
        )
    
    def _generate_adversarial_summary(self, findings: Dict[str, Any]) -> str:
        """Generate summary for adversarial audit"""
        attacks = len(findings.get('assumption_attacks', []))
        failures = len(findings.get('failure_modes', []))
        
        return (
            f"Adversarial audit: {attacks} assumptions challenged, "
            f"{failures} failure modes identified."
        )


