"""
Strategy Evolution Engine (Stage 5)

Genetic programming system for automated strategy discovery and optimization.

This module uses evolutionary algorithms to automatically generate, test, and
optimize trading strategies by combining cycle analysis, regime filtering,
volatility management, and risk controls.

Features:
- Strategy genome encoding (DNA of a strategy)
- Rule library (FLD, VTL, cycle, volatility, risk filters)
- Fitness evaluation (Sharpe, drawdown, returns)
- Genetic operations (crossover, mutation)
- Evolutionary optimization
- Backtesting framework
- Progress visualization

This is how professional quant funds discover new edges without manual trial-and-error.

Author: Meridian Team
Date: December 4, 2025
Stage: 5 of 10
"""

from .genome import StrategyGenome
from .rule_library import RuleLibrary
from .evaluator import StrategyEvaluator
from .genetic_engine import GeneticStrategyEngine
from .backtester import StrategyBacktester

# Optional: Dashboard
try:
    from .dashboard import plot_strategy_evolution_dashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    plot_strategy_evolution_dashboard = None
    _DASHBOARD_AVAILABLE = False

__all__ = [
    'StrategyGenome',
    'RuleLibrary',
    'StrategyEvaluator',
    'GeneticStrategyEngine',
    'StrategyBacktester',
    'plot_strategy_evolution_dashboard',
]

__version__ = '1.0.0'

