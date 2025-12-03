"""
Incubation Platform for Meridian v2.1.2

Automated strategy promotion: Research → WFA → Paper → Live
"""

from .incubator_state import StrategyState, StrategyStatus, load_strategy_state, save_strategy_state
from .promotion_rules import evaluate_promotion, can_promote_to_paper, can_promote_to_live
from .demotion_rules import evaluate_demotion, should_demote_to_disabled
from .incubation_runner import run_incubation_cycle, update_strategy_state
from .incubation_reporter import IncubationReporter, generate_incubation_report

__all__ = [
    'StrategyState',
    'StrategyStatus',
    'load_strategy_state',
    'save_strategy_state',
    'evaluate_promotion',
    'can_promote_to_paper',
    'can_promote_to_live',
    'evaluate_demotion',
    'should_demote_to_disabled',
    'run_incubation_cycle',
    'update_strategy_state',
    'IncubationReporter',
    'generate_incubation_report',
]

