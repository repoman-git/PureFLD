"""
Sweep Grid Generator for Meridian v2.1.2

Generates parameter combinations for optimization.
"""

import itertools
import random
from typing import List, Dict, Any

from .sweep_config import SweepConfig, SweepMode


class SweepGrid:
    """
    Generates parameter combinations for sweep.
    
    Supports:
    - Grid search (cartesian product)
    - Random search
    - Custom parameter sets
    """
    
    def __init__(self, config: SweepConfig):
        """
        Initialize sweep grid generator.
        
        Args:
            config: SweepConfig instance
        """
        self.config = config
    
    def generate(self) -> List[Dict[str, Any]]:
        """
        Generate parameter combinations.
        
        Returns:
            List of parameter dictionaries
        """
        if self.config.mode == SweepMode.GRID:
            return self._generate_grid()
        elif self.config.mode == SweepMode.RANDOM:
            return self._generate_random()
        else:
            raise ValueError(f"Unsupported sweep mode: {self.config.mode}")
    
    def _generate_grid(self) -> List[Dict[str, Any]]:
        """Generate full grid search"""
        # Build parameter space
        param_space = {
            'fld_offset': self.config.fld_offsets,
            'fld_smoothing': self.config.fld_smoothing,
            'cot_threshold': self.config.cot_thresholds,
            'cot_lookback': self.config.cot_lookback,
            'tdom_filter': self.config.tdom_filter_enabled,
            'tdom_threshold': self.config.tdom_threshold,
            'slippage_bps': self.config.slippage_bps,
        }
        
        # Generate cartesian product
        keys = list(param_space.keys())
        values = list(param_space.values())
        
        combinations = []
        for combo in itertools.product(*values):
            param_dict = dict(zip(keys, combo))
            combinations.append(param_dict)
        
        # Apply max combinations limit
        if len(combinations) > self.config.max_combinations:
            print(f"⚠️ Limiting combinations from {len(combinations)} to {self.config.max_combinations}")
            combinations = combinations[:self.config.max_combinations]
        
        return combinations
    
    def _generate_random(self) -> List[Dict[str, Any]]:
        """Generate random search"""
        random.seed(self.config.random_seed)
        
        combinations = []
        
        for _ in range(self.config.random_samples):
            param_dict = {
                'fld_offset': random.choice(self.config.fld_offsets),
                'fld_smoothing': random.choice(self.config.fld_smoothing),
                'cot_threshold': random.choice(self.config.cot_thresholds),
                'cot_lookback': random.choice(self.config.cot_lookback),
                'tdom_filter': random.choice(self.config.tdom_filter_enabled),
                'tdom_threshold': random.choice(self.config.tdom_threshold),
                'slippage_bps': random.choice(self.config.slippage_bps),
            }
            combinations.append(param_dict)
        
        return combinations
    
    def get_parameter_count(self) -> int:
        """Get total number of parameters"""
        return len(self.generate())

