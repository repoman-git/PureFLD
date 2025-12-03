"""
Audit Engine for Meridian v2.1.2

Multi-AI verification and self-audit system.
Prevents hallucinations, ensures transparency, provides regulatory safety.
"""

from .audit_orchestrator import AuditOrchestrator, AuditResult
from .audit_modes import AuditMode, NeutralAudit, AdversarialAudit, CrossModelAudit
from .model_profiles import ModelProfile, get_model_profile
from .report_builder import build_audit_report, AuditReportFormat

__all__ = [
    'AuditOrchestrator',
    'AuditResult',
    'AuditMode',
    'NeutralAudit',
    'AdversarialAudit',
    'CrossModelAudit',
    'ModelProfile',
    'get_model_profile',
    'build_audit_report',
    'AuditReportFormat',
]

