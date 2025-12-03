"""
AI Module for Meridian v2.1.2

Strategy suggestion and optimization scaffolding.
Provides rule-based recommendations (LLM integration ready).
"""

from .strategy_suggester import (
    suggest_strategy_improvements,
    generate_improvement_report
)
from .strategy_feedback import (
    ai_feedback,
    critique_candidate
)

__all__ = [
    'suggest_strategy_improvements',
    'generate_improvement_report',
    'ai_feedback',
    'critique_candidate',
]

