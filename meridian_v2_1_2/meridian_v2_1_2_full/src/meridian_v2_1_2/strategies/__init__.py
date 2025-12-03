"""
Strategies Module

Collection of trading strategies for different asset classes.
"""

# ETF Strategies
try:
    from .etf import FLD_ETF, MomentumETF, CycleETF, DefensiveETF, HurstETF
    ETF_STRATEGIES = {
        'FLD-ETF': FLD_ETF,
        'Momentum-ETF': MomentumETF,
        'Cycle-ETF': CycleETF,
        'Defensive-ETF': DefensiveETF,
        'Hurst-ETF': HurstETF
    }
except ImportError:
    ETF_STRATEGIES = {}

__all__ = ['ETF_STRATEGIES']

