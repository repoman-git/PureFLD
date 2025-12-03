"""
Multi-AI Research Agent Framework

Specialized AI agents for strategy analysis and research.
LLM-agnostic scaffolding (currently rule-based, LLM-ready).
"""

from .core import ResearchAgent, AgentInsight
from .roles import (
    CycleAnalysisAgent,
    FLDInspectorAgent,
    BacktestCriticAgent,
    RiskProfilerAgent,
    ParameterScientistAgent,
    StrategyGeneratorAgent,
    DocumentationAgent,
    COTAnalysisAgent,
    MarketRegimeAgent,
    PerformanceAuditorAgent
)
from .orchestrator import ResearchOrchestrator

__all__ = [
    'ResearchAgent',
    'AgentInsight',
    'CycleAnalysisAgent',
    'FLDInspectorAgent',
    'BacktestCriticAgent',
    'RiskProfilerAgent',
    'ParameterScientistAgent',
    'StrategyGeneratorAgent',
    'DocumentationAgent',
    'COTAnalysisAgent',
    'MarketRegimeAgent',
    'PerformanceAuditorAgent',
    'ResearchOrchestrator',
]

