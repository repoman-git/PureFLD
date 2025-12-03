"""
Synthetic Dataset Wrapper for Meridian v2.1.2

Complete synthetic market generation.
"""

import pandas as pd
from typing import Dict
from .synth_regimes import generate_regime_sequence
from .synth_price_generator import generate_synthetic_prices
from .synth_cot import generate_synthetic_cot
from .synth_yields import generate_synthetic_yields
from .synth_macro import generate_synthetic_macro


class SyntheticDataset:
    """
    Complete synthetic dataset generator.
    
    Generates all data needed to run Meridian end-to-end:
    - Prices (GLD, LTPZ, etc.)
    - COT data
    - Real yields
    - Macro indicators
    - Regime sequences
    """
    
    def __init__(self, config=None):
        """
        Initialize dataset generator.
        
        Args:
            config: SyntheticConfig or MeridianConfig
        """
        if config is None:
            from ..config import SyntheticConfig
            self.config = SyntheticConfig()
        elif hasattr(config, 'synthetic'):
            self.config = config.synthetic
        else:
            self.config = config
    
    def generate(self, symbols: list = None) -> Dict[str, pd.DataFrame]:
        """
        Generate complete synthetic dataset.
        
        Args:
            symbols: List of symbols to generate (default: ['GLD', 'LTPZ'])
        
        Returns:
            Dict containing all generated data
        """
        if symbols is None:
            symbols = ['GLD', 'LTPZ']
        
        length = self.config.length_days
        seed = self.config.seed
        
        # Generate regime sequence
        regime_seq = generate_regime_sequence(
            length,
            switch_prob=self.config.regime_switch_prob,
            seed=seed
        )
        
        # Generate prices for each symbol
        prices = {}
        for symbol in symbols:
            prices[symbol] = generate_synthetic_prices(
                symbol=symbol,
                length=length,
                start_price=100.0,
                vol_low=self.config.vol_low,
                vol_high=self.config.vol_high,
                trend_strength=self.config.trend_strength,
                cycle_amp=self.config.cycle_amp,
                cycle_period=self.config.cycle_period,
                regime_sequence=regime_seq,
                seed=seed + hash(symbol) % 1000
            )
        
        # Generate COT data
        cot = generate_synthetic_cot(
            length=length,
            noise=self.config.cot_noise,
            trendiness=self.config.cot_trendiness,
            regime_sequence=regime_seq,
            seed=seed
        )
        
        # Generate real yields
        real_yields = generate_synthetic_yields(
            length=length,
            amplitude=self.config.real_yield_amp,
            shock_probability=self.config.real_yield_shock_probability,
            gold_correlation=self.config.gold_yield_corr,
            regime_sequence=regime_seq,
            seed=seed
        )
        
        # Generate macro data
        macro = generate_synthetic_macro(
            length=length,
            shock_probability=self.config.real_yield_shock_probability,
            regime_sequence=regime_seq,
            seed=seed
        )
        
        return {
            'prices': prices,
            'cot': cot,
            'real_yields': real_yields,
            'macro': macro,
            'regimes': regime_seq
        }
    
    def generate_stress_scenario(self, scenario: str) -> Dict[str, pd.DataFrame]:
        """
        Generate specific stress scenarios.
        
        Scenarios:
        - 'crash': Severe downtrend with high vol
        - 'stagflation': Rising inflation + falling growth
        - 'yield_spike': Sudden real yield surge
        - 'cycle_collapse': Cycle amplitude collapse
        
        Args:
            scenario: Scenario name
        
        Returns:
            Dict containing stressed data
        """
        # Modify config for stress scenarios
        if scenario == 'crash':
            self.config.vol_high = 0.05  # 5% daily vol
            self.config.trend_strength = -0.8  # Strong downtrend
        
        elif scenario == 'stagflation':
            self.config.real_yield_shock_probability = 0.1
            self.config.trend_strength = -0.2
        
        elif scenario == 'yield_spike':
            self.config.real_yield_amp = 2.0
            self.config.real_yield_shock_probability = 0.05
        
        elif scenario == 'cycle_collapse':
            self.config.cycle_amp = 0.005  # Weak cycles
            self.config.cycle_deform = False
        
        return self.generate()

