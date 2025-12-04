"""
Multi-Agent AI Coordinator (Stage 9)

AI orchestration layer for semi-autonomous operation.

This module creates specialized AI agents that analyze, recommend, and explain
Meridian's cycle intelligence, making the system self-orchestrating.

Agents:
- CycleAnalyst: Analyzes Hurst phasing, FLD, VTL
- HarmonicSpecialist: Spectral analysis expert
- Forecaster: Generates predictions and explanations
- IntermarketAnalyst: Cross-market relationships
- RiskManager: Risk assessment and recommendations
- StrategyWriter: Natural language trade explanations
- BacktestReviewer: Performance critique and improvement suggestions
- ExecutionMonitor: Trade monitoring and summaries

This is the "Meridian Brain" - AI-first quant platform.

Author: Meridian Team
Date: December 4, 2025
Stage: 9 of 10
"""

from .agent_orchestrator import AgentOrchestrator

__all__ = ['AgentOrchestrator']

__version__ = '1.0.0'

