"""
Meta-Learning Engine for Meridian v2.1.2

Adaptive strategy weighting, reinforcement scoring, and intelligent weight adjustment.
"""

from .reward_tracker import compute_strategy_rewards, track_rolling_rewards
from .weight_adapter import adapt_weights, apply_weight_constraints
from .confidence_model import compute_signal_confidence, compute_strategy_confidence
from .regime_responder import adapt_weights_by_regime
from .meta_strategy_manager import MetaStrategyManager

__all__ = [
    'compute_strategy_rewards',
    'track_rolling_rewards',
    'adapt_weights',
    'apply_weight_constraints',
    'compute_signal_confidence',
    'compute_strategy_confidence',
    'adapt_weights_by_regime',
    'MetaStrategyManager',
]

