"""
Regime/Cycle/COT Blending Integration Test

Tests multi-signal integration.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.synthetic import (
    SyntheticDataset,
    generate_cycle_component,
    generate_regime_sequence
)
from meridian_v2_1_2.regimes import classify_volatility, classify_trend
from meridian_v2_1_2.cycles import compute_cycle_phase_normalized


class TestRegimeCycleCOTBlending:
    """Test multi-signal integration"""
    
    def test_regime_engine_on_synthetic_data(self):
        """Test regime classification works on synthetic data"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD'])
        
        prices = data['prices']['GLD']['close']
        
        # Classify volatility regime
        vol_regime = classify_volatility(prices, cfg.regimes)
        
        assert len(vol_regime) == len(prices)
        assert vol_regime.isin([0, 1, 2]).all()
        
        # Classify trend regime
        trend_regime = classify_trend(prices, cfg.regimes)
        
        assert len(trend_regime) == len(prices)
        assert trend_regime.isin([-1, 0, 1]).all()
    
    def test_cycle_engine_on_synthetic_cycles(self):
        """Test cycle detection on known synthetic cycles"""
        cycle = generate_cycle_component(length=500, period=120, deform=False)
        cycle_series = pd.Series(cycle, index=pd.date_range('2020-01-01', periods=500))
        
        cfg = MeridianConfig()
        phase = compute_cycle_phase_normalized(cycle_series, cycle_length=120)
        
        # Phase should be between 0 and 1
        assert len(phase) > 0
        assert (phase >= 0).all()
        assert (phase <= 1).all()
    
    def test_cot_data_integrates_with_signals(self):
        """Test COT data can be used in signal generation"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD'])
        
        cot = data['cot']
        
        # COT should have correct structure
        assert 'commercials_net' in cot.columns
        assert 'non_commercials_net' in cot.columns
        
        # Can compute COT indicator
        cot_signal = (cot['commercials_net'] > cot['commercials_net'].median()).astype(float)
        
        assert len(cot_signal) > 0
    
    def test_real_yields_affect_ltpz_logic(self):
        """Test real yields data integrates with LTPZ inverse logic"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD', 'LTPZ'])
        
        yields = data['real_yields']
        
        # Real yields should have regime classification
        assert 'real_yield_regime' in yields.columns
        
        # When real yields rising, LTPZ should be favored (inverse gold)
        rising_periods = yields['real_yield_regime'] == 'rising'
        
        # This is the logic your strategy would use
        assert rising_periods.sum() > 0

