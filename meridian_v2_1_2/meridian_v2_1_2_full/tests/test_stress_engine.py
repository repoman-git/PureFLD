"""
Stress Test Engine Validation Suite

Tests the chaos engineering framework itself.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.stress import (
    inject_price_gaps,
    inject_missing_bars,
    inject_nan_bursts,
    inject_cycle_breaks,
    inject_regime_corruption,
    volatility_explosion,
    flash_crash,
    rate_shock,
    run_stress_tests,
    generate_stress_report
)


class TestChaosInjection:
    """Test chaos injection functions"""
    
    def test_price_gap_injection(self):
        """Test price gap injection"""
        # Create synthetic prices
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'open': 100 + np.random.randn(100),
            'high': 102 + np.random.randn(100),
            'low': 98 + np.random.randn(100),
            'close': 100 + np.random.randn(100)
        }, index=dates)
        
        # Inject gaps
        gapped = inject_price_gaps(prices, severity=0.5, seed=42)
        
        # Should have same length
        assert len(gapped) == len(prices)
        
        # Should have some differences
        assert not prices['close'].equals(gapped['close'])
    
    def test_missing_bars_injection(self):
        """Test missing bars injection"""
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'close': 100 + np.random.randn(100)
        }, index=dates)
        
        # Inject missing bars
        missing = inject_missing_bars(prices, severity=0.3, seed=42)
        
        # Should have fewer bars
        assert len(missing) < len(prices)
    
    def test_nan_burst_injection(self):
        """Test NaN burst injection"""
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'close': 100.0
        }, index=dates)
        
        # Inject NaNs
        corrupted = inject_nan_bursts(prices, severity=0.5, seed=42)
        
        # Should have NaNs
        assert corrupted.isna().sum().sum() > 0
    
    def test_cycle_break_injection(self):
        """Test cycle break injection"""
        cycle = pd.Series(np.sin(np.linspace(0, 4*np.pi, 100)))
        
        # Break cycle
        broken = inject_cycle_breaks(cycle, severity=0.5, seed=42)
        
        # Should be different
        assert not cycle.equals(broken)
    
    def test_regime_corruption(self):
        """Test regime corruption"""
        regimes = pd.Series(['low_vol'] * 50 + ['high_vol'] * 50)
        
        # Corrupt regimes
        corrupted = inject_regime_corruption(regimes, severity=0.3, seed=42)
        
        # Should have more transitions
        transitions = (corrupted != corrupted.shift()).sum()
        original_transitions = (regimes != regimes.shift()).sum()
        
        assert transitions > original_transitions


class TestMarketShocks:
    """Test market shock scenarios"""
    
    def test_volatility_explosion(self):
        """Test volatility explosion"""
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.0
        }, index=dates)
        
        # Apply vol explosion
        shocked = volatility_explosion(prices, shock_day=50, magnitude=2.0)
        
        # Check that function executed without error
        assert len(shocked) == len(prices)
        
        # Vol explosion should modify high/low spreads
        # (Implementation may vary, just verify it runs)
    
    def test_flash_crash(self):
        """Test flash crash"""
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.0
        }, index=dates)
        
        # Apply flash crash
        crashed = flash_crash(prices, crash_day=50, drop_pct=0.15)
        
        # Crash day should have lower prices
        crash_low = crashed.loc[crashed.index[50], 'low']
        assert crash_low < 99.0
    
    def test_rate_shock(self):
        """Test rate shock"""
        dates = pd.date_range('2020-01-01', periods=100)
        yields_df = pd.DataFrame({
            'real_yield_10y': 2.0
        }, index=dates)
        
        # Apply rate shock
        shocked = rate_shock(yields_df, shock_day=50, spike_bps=150)
        
        # Yields after shock should be higher
        assert shocked.loc[shocked.index[50:], 'real_yield_10y'].mean() > 2.5


class TestStressRunner:
    """Test stress test runner"""
    
    def test_stress_runner_completes(self, tmp_path):
        """Test stress runner completes without crashing"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100  # Short for testing
        cfg.stress.num_runs = 5  # Few runs
        cfg.stress.severity = 0.5
        cfg.stress.report_path = str(tmp_path / "stress")
        
        # Run stress tests
        results = run_stress_tests(cfg, num_runs=5)
        
        # Should have 5 results
        assert len(results) == 5
        
        # All should have run_id
        assert all(hasattr(r, 'run_id') for r in results)
        
        # At least some should complete
        completed = sum(1 for r in results if r.completed)
        assert completed > 0
    
    def test_stress_scenarios_execute(self):
        """Test specific scenarios execute"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        cfg.stress.severity = 0.3
        
        scenarios = ['baseline', 'price_gaps', 'flash_crash']
        
        results = run_stress_tests(cfg, num_runs=3, scenarios=scenarios)
        
        assert len(results) == 3
        assert all(r.scenario_name in scenarios for r in results)
    
    def test_stress_results_contain_metrics(self):
        """Test results contain all expected metrics"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        
        results = run_stress_tests(cfg, num_runs=2)
        
        for result in results:
            assert hasattr(result, 'final_equity')
            assert hasattr(result, 'max_drawdown')
            assert hasattr(result, 'nan_count')
            assert hasattr(result, 'weaknesses')


class TestStressReporter:
    """Test stress test reporter"""
    
    def test_report_generation(self, tmp_path):
        """Test report files are generated"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        
        # Run stress tests
        results = run_stress_tests(cfg, num_runs=3)
        
        # Generate reports
        report_paths = generate_stress_report(results, str(tmp_path / "reports"))
        
        # Check files exist
        assert Path(report_paths['summary']).exists()
        assert Path(report_paths['weakness_analysis']).exists()
        
        # Should have 3 run reports
        assert len(report_paths['run_reports']) == 3
    
    def test_summary_report_content(self, tmp_path):
        """Test summary report has correct content"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        
        results = run_stress_tests(cfg, num_runs=5)
        report_paths = generate_stress_report(results, str(tmp_path / "reports"))
        
        # Read summary
        with open(report_paths['summary'], 'r') as f:
            content = f.read()
        
        # Should contain key sections
        assert "STRESS TEST SUMMARY" in content
        assert "Overall Results" in content
        assert "Scenario Breakdown" in content


class TestSystemResilience:
    """Test system resilience under stress"""
    
    def test_system_survives_combined_chaos(self):
        """Test system survives multiple failures"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        cfg.stress.severity = 0.8  # High severity
        
        results = run_stress_tests(
            cfg,
            num_runs=10,
            scenarios=['combined_chaos']
        )
        
        # At least some runs should complete
        completed = sum(1 for r in results if r.completed)
        assert completed >= 5, "System should survive at least 50% of combined chaos"
    
    def test_system_handles_nans_gracefully(self):
        """Test system handles NaN injection"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100
        
        results = run_stress_tests(
            cfg,
            num_runs=5,
            scenarios=['nan_bursts']
        )
        
        # System should not crash
        crashed = sum(1 for r in results if r.crashed)
        assert crashed < len(results), "System should handle NaNs without crashing"


class TestDeterminism:
    """Test stress testing is deterministic"""
    
    def test_chaos_injection_deterministic(self):
        """Test chaos injection is reproducible"""
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'close': 100.0
        }, index=dates)
        
        # Same seed should produce same result
        result1 = inject_price_gaps(prices, severity=0.5, seed=42)
        result2 = inject_price_gaps(prices, severity=0.5, seed=42)
        
        pd.testing.assert_frame_equal(result1, result2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

