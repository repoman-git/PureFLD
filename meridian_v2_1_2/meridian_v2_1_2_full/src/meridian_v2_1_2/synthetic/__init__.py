"""
Synthetic Market Generator for Meridian v2.1.2

Create realistic-but-fictional markets for stress testing.
"""

from .synth_price_generator import generate_synthetic_prices
from .synth_volatility import generate_volatility_regime, generate_stochastic_vol
from .synth_trends import generate_trend_component
from .synth_cycles import generate_cycle_component
from .synth_macro import generate_synthetic_macro
from .synth_cot import generate_synthetic_cot
from .synth_yields import generate_synthetic_yields
from .synth_regimes import generate_regime_sequence, MarketRegime
from .synthetic_dataset import SyntheticDataset

__all__ = [
    'generate_synthetic_prices',
    'generate_volatility_regime',
    'generate_stochastic_vol',
    'generate_trend_component',
    'generate_cycle_component',
    'generate_synthetic_macro',
    'generate_synthetic_cot',
    'generate_synthetic_yields',
    'generate_regime_sequence',
    'MarketRegime',
    'SyntheticDataset',
]


