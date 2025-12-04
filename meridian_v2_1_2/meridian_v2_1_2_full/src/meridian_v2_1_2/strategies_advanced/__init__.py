"""
Advanced Strategy System (Scaffold)

Future-proof architecture for:
- Auto strategy generation
- Strategy mutation
- Multi-strategy comparison
- Strategy fitness scoring
- Meta-learning feedback loops

⚠️  STUBS ONLY - Placeholders for future phases
"""

from .strategy_profiles import describe_strategy, get_strategy_profile
from .strategy_mutation_engine import mutate_strategy, create_strategy_variant
from .strategy_auto_optimizer import optimize_strategy_params, auto_tune
from .strategy_explainability import explain_strategy_decision, generate_rule_breakdown
from .strategy_comparison import compare_strategies, rank_strategies
from .strategy_integrity_score import evaluate_strategy_fitness, calculate_integrity_score

__all__ = [
    'describe_strategy',
    'get_strategy_profile',
    'mutate_strategy',
    'create_strategy_variant',
    'optimize_strategy_params',
    'auto_tune',
    'explain_strategy_decision',
    'generate_rule_breakdown',
    'compare_strategies',
    'rank_strategies',
    'evaluate_strategy_fitness',
    'calculate_integrity_score',
]


