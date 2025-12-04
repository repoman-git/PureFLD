#!/usr/bin/env python3
"""
Quick validation script for TDOM v1 integration.
This script tests the core functionality without requiring pytest.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from meridian_v2_1_2 import MeridianConfig, run_backtest, compute_tdom_flags

def test_config():
    """Test configuration system"""
    print("=" * 60)
    print("TEST 1: Configuration System")
    print("=" * 60)
    
    config = MeridianConfig()
    assert hasattr(config, 'seasonality'), "Missing seasonality config"
    assert hasattr(config.seasonality, 'use_tdom'), "Missing use_tdom field"
    assert hasattr(config.seasonality, 'favourable_days'), "Missing favourable_days"
    assert hasattr(config.seasonality, 'unfavourable_days'), "Missing unfavourable_days"
    
    print("✅ MeridianConfig created successfully")
    print(f"   - use_tdom: {config.seasonality.use_tdom}")
    print(f"   - favourable_days: {config.seasonality.favourable_days}")
    print(f"   - unfavourable_days: {config.seasonality.unfavourable_days}")
    print()

def test_tdom_flags():
    """Test TDOM flag computation"""
    print("=" * 60)
    print("TEST 2: TDOM Flag Computation")
    print("=" * 60)
    
    dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
    tdom = compute_tdom_flags(dates, favourable_days=[1, 2, 3], unfavourable_days=[5, 6])
    
    assert tdom.loc['2020-01-01'] == 1, "Day 1 should be favourable"
    assert tdom.loc['2020-01-02'] == 1, "Day 2 should be favourable"
    assert tdom.loc['2020-01-03'] == 1, "Day 3 should be favourable"
    assert tdom.loc['2020-01-04'] == 0, "Day 4 should be neutral"
    assert tdom.loc['2020-01-05'] == -1, "Day 5 should be unfavourable"
    assert tdom.loc['2020-01-06'] == -1, "Day 6 should be unfavourable"
    
    print("✅ TDOM flags computed correctly")
    print(f"   - Favourable days (1,2,3): {(tdom == 1).sum()} flags")
    print(f"   - Unfavourable days (5,6): {(tdom == -1).sum()} flags")
    print(f"   - Neutral days: {(tdom == 0).sum()} flags")
    print()

def test_orchestrator():
    """Test orchestrator integration"""
    print("=" * 60)
    print("TEST 3: Orchestrator Integration")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range('2020-01-01', periods=30, freq='D')
    prices = pd.Series(range(1500, 1530), index=dates, name='close')
    
    # Test with TDOM enabled
    config = MeridianConfig()
    config.seasonality.use_tdom = True
    config.seasonality.favourable_days = [1, 2, 3]
    config.strategy.use_tdom = True
    
    results = run_backtest(config, prices)
    
    assert 'tdom' in results, "Missing TDOM in results"
    assert results['tdom'] is not None, "TDOM should be computed"
    assert len(results['tdom']) == len(prices), "TDOM length mismatch"
    
    print("✅ Orchestrator integration successful")
    print(f"   - TDOM computed: {results['tdom'] is not None}")
    print(f"   - TDOM length: {len(results['tdom'])}")
    print(f"   - Total signals: {results['stats']['total_trades']}")
    print()
    
    # Test with TDOM disabled
    config.seasonality.use_tdom = False
    results_no_tdom = run_backtest(config, prices)
    
    assert results_no_tdom['tdom'] is None, "TDOM should not be computed when disabled"
    
    print("✅ TDOM correctly disabled when configured")
    print()

def test_strategy_gating():
    """Test strategy TDOM gating"""
    print("=" * 60)
    print("TEST 4: Strategy TDOM Gating")
    print("=" * 60)
    
    from meridian_v2_1_2.strategy import FLDStrategy, StrategyConfig
    
    # Create test data with clear crossover
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    prices = pd.Series([95, 95, 105, 105, 105, 105, 105, 105, 105, 105], index=dates)
    fld = pd.Series([100] * 10, index=dates)
    
    # TDOM with day 3 unfavourable
    tdom = pd.Series([1, 1, -1, 0, 0, 0, 0, 0, 0, 0], index=dates)
    
    # Test with TDOM enabled
    config = StrategyConfig(use_tdom=True)
    strategy = FLDStrategy(config)
    signals = strategy.generate_signals(prices, fld, tdom_series=tdom)
    
    # Signal on day 3 (unfavourable) should be blocked
    assert signals.loc[dates[2], 'signal'] == 0, "Signal should be blocked on unfavourable day"
    
    print("✅ Strategy TDOM gating working correctly")
    print(f"   - Signal on unfavourable day (day 3): {signals.loc[dates[2], 'signal']} (should be 0)")
    print(f"   - Total signals generated: {(signals['signal'] != 0).sum()}")
    print()

def test_determinism():
    """Test deterministic behavior"""
    print("=" * 60)
    print("TEST 5: Deterministic Behavior")
    print("=" * 60)
    
    dates = pd.date_range('2020-01-01', periods=20, freq='D')
    prices = pd.Series(range(1500, 1520), index=dates)
    
    config = MeridianConfig()
    config.seasonality.use_tdom = True
    
    results1 = run_backtest(config, prices)
    results2 = run_backtest(config, prices)
    
    assert results1['signals'].equals(results2['signals']), "Results should be deterministic"
    assert results1['tdom'].equals(results2['tdom']), "TDOM should be deterministic"
    
    print("✅ Deterministic behavior verified")
    print("   - Multiple runs produce identical results")
    print()

def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("MERIDIAN v2.1.2 - TDOM v1 INTEGRATION VALIDATION")
    print("=" * 60)
    print()
    
    try:
        test_config()
        test_tdom_flags()
        test_orchestrator()
        test_strategy_gating()
        test_determinism()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED - TDOM v1 INTEGRATION COMPLETE!")
        print("=" * 60)
        print()
        print("✅ Configuration system working")
        print("✅ TDOM flag computation working")
        print("✅ Orchestrator integration working")
        print("✅ Strategy gating working")
        print("✅ Deterministic behavior verified")
        print()
        print("Next steps:")
        print("  - Run full pytest suite: pytest tests/test_seasonality_integration.py -v")
        print("  - Try the demo notebook: notebooks/tdom_integration_demo.ipynb")
        print("  - Use CLI: python scripts/meridian_control.py --help")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())


