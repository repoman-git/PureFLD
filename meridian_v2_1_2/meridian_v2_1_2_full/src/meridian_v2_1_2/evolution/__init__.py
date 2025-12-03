"""
Evolution Module for Meridian v2.1.2

Genetic algorithm-based strategy evolution and optimization.
"""

from .evolution_engine import (
    evolve_strategy,
    EvolutionResult,
    evaluate_candidate,
    export_best_to_dict
)
from .param_spaces import (
    FLD_PARAM_SPACE,
    COT_PARAM_SPACE,
    GENERIC_PARAM_SPACE,
    get_param_space,
    validate_params
)

__all__ = [
    'evolve_strategy',
    'EvolutionResult',
    'evaluate_candidate',
    'export_best_to_dict',
    'FLD_PARAM_SPACE',
    'COT_PARAM_SPACE',
    'GENERIC_PARAM_SPACE',
    'get_param_space',
    'validate_params',
]

