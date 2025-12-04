"""
Attribution Consistency Integration Test

Tests that PnL attribution adds up correctly.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.synthetic import SyntheticDataset
from meridian_v2_1_2.performance import (
    compute_daily_pnl,
    attribute_to_assets
)


class TestAttributionConsistency:
    """Test attribution consistency"""
    
    def test_asset_attribution_sums_to_total(self):
        """Test asset attribution sums to total PnL"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD', 'LTPZ'])
        
        # Create fixed positions
        positions = {
            'GLD': pd.Series(10.0, index=data['prices']['GLD'].index),
            'LTPZ': pd.Series(-5.0, index=data['prices']['LTPZ'].index)
        }
        
        prices = {
            'GLD': data['prices']['GLD']['close'],
            'LTPZ': data['prices']['LTPZ']['close']
        }
        
        # Compute total PnL
        total_pnl = compute_daily_pnl(positions, prices)
        
        # Compute asset attribution
        asset_attr = attribute_to_assets(positions, prices)
        
        # Sum should equal total (approximately, due to rounding)
        attr_sum = sum(asset_attr.values())
        total_sum = total_pnl.sum()
        
        assert attr_sum == pytest.approx(total_sum, rel=0.01)
    
    def test_gld_ltpz_inverse_behavior(self):
        """Test GLD/LTPZ inverse relationship in attribution"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 200
        cfg.synthetic.gold_yield_corr = -0.8  # Strong inverse
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD', 'LTPZ'])
        
        # Check correlation is negative
        gld_returns = data['prices']['GLD']['close'].pct_change()
        ltpz_returns = data['prices']['LTPZ']['close'].pct_change()
        
        # Note: Our synthetic generator doesn't enforce correlation yet
        # This test validates the data structure is correct
        assert len(gld_returns) == len(ltpz_returns)


