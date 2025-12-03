"""
Comprehensive test suite for Multi-Strategy Engine in Meridian v2.1.2.

Tests verify strategy stacking, signal blending, voting, and meta-strategy orchestration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.config import MetaStrategyConfig
from meridian_v2_1_2.multi_strategy import (
    StrategyRegistry,
    StrategyWrapper,
    blend_signals,
    vote_signals,
    compute_strategy_weights
)


def create_test_signals(length=10):
    """Create synthetic strategy signals"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestStrategyRegistry:
    """Test strategy registry"""
    
    def test_register_and_retrieve_strategy(self):
        """
        TEST 1: Register and retrieve strategies
        """
        registry = StrategyRegistry()
        
        # Register a mock strategy
        class MockStrategy:
            def generate_signals(self):
                return pd.Series([1, 0, -1])
        
        registry.register('trend', MockStrategy)
        
        # Retrieve
        strategy = registry.get('trend')
        assert strategy is MockStrategy
    
    def test_enable_disable_strategy(self):
        """
        TEST: Enable/disable strategies
        """
        registry = StrategyRegistry()
        
        class MockStrategy:
            pass
        
        registry.register('cycles', MockStrategy)
        
        # Should be enabled by default
        assert registry.is_enabled('cycles')
        
        # Disable
        registry.disable('cycles')
        assert not registry.is_enabled('cycles')
        
        # Enable again
        registry.enable('cycles')
        assert registry.is_enabled('cycles')
    
    def test_list_strategies(self):
        """
        TEST: List all and enabled strategies
        """
        registry = StrategyRegistry()
        
        class MockStrategy:
            pass
        
        registry.register('trend', MockStrategy)
        registry.register('cycles', MockStrategy)
        registry.register('seasonal', MockStrategy)
        
        registry.disable('cycles')
        
        # List all
        all_strategies = registry.list_strategies()
        assert len(all_strategies) == 3
        
        # List enabled
        enabled = registry.list_enabled()
        assert len(enabled) == 2
        assert 'cycles' not in enabled


class TestWeightedBlending:
    """Test weighted signal blending"""
    
    def test_equal_weight_blend(self):
        """
        TEST 2: Equal weight blending
        """
        dates = create_test_signals(10)
        
        # All strategies say long
        strategy_signals = {
            'trend': pd.Series([1] * 10, index=dates),
            'cycles': pd.Series([1] * 10, index=dates),
            'seasonal': pd.Series([1] * 10, index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='weighted',
            strategy_weights={'trend': 1.0, 'cycles': 1.0, 'seasonal': 1.0}
        )
        
        blended = blend_signals(strategy_signals, config)
        
        # All agree on long → should be long
        assert (blended == 1).all()
    
    def test_custom_weight_blend(self):
        """
        TEST: Custom weight blending favors heavier strategies
        """
        dates = create_test_signals(5)
        
        # Trend says long (weight 2.0)
        # Cycles says short (weight 1.0)
        strategy_signals = {
            'trend': pd.Series([1, 1, 1, 1, 1], index=dates),
            'cycles': pd.Series([-1, -1, -1, -1, -1], index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='weighted',
            strategy_weights={'trend': 2.0, 'cycles': 1.0}
        )
        
        blended = blend_signals(strategy_signals, config)
        
        # Trend has 2× weight → should win → long
        assert (blended == 1).all()


class TestVotingBlending:
    """Test voting-based signal blending"""
    
    def test_voting_threshold_behavior(self):
        """
        TEST 3: Voting threshold controls signal generation
        """
        dates = create_test_signals(5)
        
        # 2 long, 1 short, 1 flat → 50% long
        strategy_signals = {
            'trend': pd.Series([1, 1, 1, 1, 1], index=dates),
            'cycles': pd.Series([1, -1, -1, 0, 0], index=dates),
            'seasonal': pd.Series([1, 0, -1, 1, -1], index=dates),
            'cot': pd.Series([0, 0, -1, 0, 1], index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='voting',
            voting_threshold=0.5
        )
        
        blended = blend_signals(strategy_signals, config)
        
        # Bar 0: 3/4 long (75%) → +1
        assert blended.iloc[0] == 1
    
    def test_voting_draw_cases(self):
        """
        TEST: Voting draws with threshold > 0.5 result in flat
        """
        dates = create_test_signals(3)
        
        # Equal long and short votes
        strategy_signals = {
            'trend': pd.Series([1, 1, -1], index=dates),
            'cycles': pd.Series([-1, -1, 1], index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='voting',
            voting_threshold=0.6  # Require >50% to avoid ties
        )
        
        blended = blend_signals(strategy_signals, config)
        
        # Bar 0: 50% long, 50% short → need 60% → flat
        assert blended.iloc[0] == 0


class TestOverrideBlending:
    """Test override-based signal blending"""
    
    def test_override_priority_order(self):
        """
        TEST 4: Override respects priority order
        """
        dates = create_test_signals(5)
        
        strategy_signals = {
            'trend': pd.Series([0, 1, 0, 1, 0], index=dates),
            'cycles': pd.Series([1, 0, 1, 0, 1], index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='override',
            strategies_enabled=['trend', 'cycles']  # Trend has priority
        )
        
        blended = blend_signals(strategy_signals, config)
        
        # Bar 0: trend=0, cycles=1 → cycles wins → +1
        assert blended.iloc[0] == 1
        
        # Bar 1: trend=1, cycles=0 → trend wins → +1
        assert blended.iloc[1] == 1


class TestGatingBlending:
    """Test gating (AND-logic) blending"""
    
    def test_gating_requires_all_agree(self):
        """
        TEST 5: Gating requires all strategies to agree
        """
        dates = create_test_signals(5)
        
        strategy_signals = {
            'trend': pd.Series([1, 1, 1, 0, 1], index=dates),
            'cycles': pd.Series([1, 0, 1, 1, -1], index=dates),
            'seasonal': pd.Series([1, 1, 0, 1, 1], index=dates)
        }
        
        config = MetaStrategyConfig(blend_mode='gating')
        
        blended = blend_signals(strategy_signals, config)
        
        # Bar 0: All say 1 → +1
        assert blended.iloc[0] == 1
        
        # Bar 1: cycles=0, others=1 → blocked → 0
        assert blended.iloc[1] == 0
        
        # Bar 4: trend=1, cycles=-1 → conflict → 0
        assert blended.iloc[4] == 0


class TestWeightingEngine:
    """Test strategy weight computation"""
    
    def test_compute_normalized_weights(self):
        """
        TEST 6: Weights are normalized to sum to 1.0
        """
        strategy_names = ['trend', 'cycles', 'seasonal']
        config_weights = {'trend': 2.0, 'cycles': 1.0, 'seasonal': 1.0}
        
        weights = compute_strategy_weights(strategy_names, config_weights=config_weights)
        
        # Should sum to 1.0
        assert abs(sum(weights.values()) - 1.0) < 0.001
        
        # Trend should have 2/4 = 0.5
        assert abs(weights['trend'] - 0.5) < 0.001


class TestDeterminism:
    """Test that multi-strategy functions are deterministic"""
    
    def test_weighted_blend_deterministic(self):
        """
        TEST 7: Weighted blending is deterministic
        """
        dates = create_test_signals(20)
        
        strategy_signals = {
            'trend': pd.Series(np.random.RandomState(42).choice([-1, 0, 1], 20), index=dates),
            'cycles': pd.Series(np.random.RandomState(43).choice([-1, 0, 1], 20), index=dates)
        }
        
        config = MetaStrategyConfig(
            blend_mode='weighted',
            strategy_weights={'trend': 0.6, 'cycles': 0.4}
        )
        
        blended1 = blend_signals(strategy_signals, config)
        blended2 = blend_signals(strategy_signals, config)
        
        pd.testing.assert_series_equal(blended1, blended2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

