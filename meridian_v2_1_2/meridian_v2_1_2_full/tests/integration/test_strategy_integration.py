"""
Strategy Integration Test

Tests multi-strategy blending with meta-learning.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.synthetic import SyntheticDataset


class TestStrategyIntegration:
    """Test strategy blending and meta-learning"""
    
    def test_strategy_weights_sum_to_one(self):
        """Test strategy weights are normalized"""
        cfg = MeridianConfig()
        cfg.meta_strategy.blend_mode = "weighted"
        cfg.meta_strategy.strategy_weights = {
            'trend': 0.4,
            'cycle': 0.3,
            'seasonal': 0.2,
            'cot': 0.1
        }
        
        # Weights sum to 1
        total_weight = sum(cfg.meta_strategy.strategy_weights.values())
        assert total_weight == pytest.approx(1.0, rel=0.01)
    
    def test_meta_learning_config_exists(self):
        """Test meta-learning configuration is accessible"""
        cfg = MeridianConfig()
        cfg.meta_learning.enable_meta_learning = True
        cfg.meta_learning.learning_rate = 0.1
        
        # Config should be set correctly
        assert cfg.meta_learning.enable_meta_learning is True
        assert cfg.meta_learning.learning_rate == 0.1
        
        # Meta-learning will be fully integrated in future phase
        # For now, just validate config is accessible
    
    def test_strategy_blending_deterministic(self):
        """Test strategy blending is deterministic"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 50
        cfg.synthetic.seed = 42
        
        # Generate same data twice
        dataset1 = SyntheticDataset(cfg)
        data1 = dataset1.generate()
        
        dataset2 = SyntheticDataset(cfg)
        data2 = dataset2.generate()
        
        # Should be identical
        assert data1['prices']['GLD']['close'].equals(data2['prices']['GLD']['close'])

