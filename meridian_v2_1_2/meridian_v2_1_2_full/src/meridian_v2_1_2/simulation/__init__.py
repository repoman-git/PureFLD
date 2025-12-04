"""
Simulation Module for Meridian v2.1.2

Probabilistic modeling, Monte Carlo simulation, and robustness testing.
"""

from .monte_carlo import (
    monte_carlo_equity_simulation,
    calculate_confidence_intervals,
    calculate_risk_of_ruin
)
from .walk_forward import (
    walk_forward_validation,
    expanding_window_validation
)

__all__ = [
    'monte_carlo_equity_simulation',
    'calculate_confidence_intervals',
    'calculate_risk_of_ruin',
    'walk_forward_validation',
    'expanding_window_validation',
]


