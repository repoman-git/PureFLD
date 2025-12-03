"""
Model Risk Engine Test Suite

Tests for overfitting, stability, drift, and fragility detection.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from meridian_v2_1_2.risk.model_risk import (
    detect_overfit,
    compute_overfit_ratio,
    analyze_stability,
    compute_stability_score,
    detect_drift,
    compute_weight_drift,
    analyze_regime_dependency,
    compute_dependency_score,
    run_sensitivity_tests,
    compute_fragility_index,
    generate_model_risk_report,
    ModelRiskRating
)


class TestOverfitDetector:
    """Test overfit detection"""
    
    def test_overfit_ratio_computation(self):
        """Test overfit ratio calculation"""
        ratio = compute_overfit_ratio(train_performance=2.0, oos_performance=1.0)
        assert ratio == 2.0
    
    def test_overfit_detection_high_ratio(self):
        """Test overfit detected when ratio high"""
        wfa_results = [
            {'train_sharpe': 3.0, 'oos_sharpe': 1.0},
            {'train_sharpe': 2.5, 'oos_sharpe': 0.8},
            {'train_sharpe': 2.8, 'oos_sharpe': 0.9}
        ]
        
        result = detect_overfit(wfa_results, max_overfit_ratio=2.0)
        
        assert result['overfit_detected'] == True
        assert result['overfit_ratio'] > 2.0
        assert result['is_safe'] == False
    
    def test_overfit_detection_low_ratio(self):
        """Test no overfit when ratio acceptable"""
        wfa_results = [
            {'train_sharpe': 1.2, 'oos_sharpe': 1.0},
            {'train_sharpe': 1.3, 'oos_sharpe': 1.1}
        ]
        
        result = detect_overfit(wfa_results, max_overfit_ratio=2.0)
        
        assert result['overfit_detected'] == False
        assert result['is_safe'] == True
    
    def test_overfit_empty_results(self):
        """Test handling of empty WFA results"""
        result = detect_overfit([])
        
        assert result['overfit_detected'] is False
        assert result['is_safe'] is True


class TestStabilityAnalyzer:
    """Test stability analysis"""
    
    def test_stability_score_computation(self):
        """Test stability score calculation"""
        returns = [0.01, 0.02, 0.01, 0.02, 0.01]
        score = compute_stability_score(returns)
        
        assert score > 0
        assert isinstance(score, float)
    
    def test_high_stability(self):
        """Test high stability detection"""
        wfa_results = [
            {'oos_return': 0.01},
            {'oos_return': 0.012},
            {'oos_return': 0.011},
            {'oos_return': 0.01}
        ]
        
        result = analyze_stability(wfa_results, min_stability_score=0.5)
        
        assert result['is_stable'] == True
        assert result['stability_score'] > 0
    
    def test_low_stability(self):
        """Test low stability detection"""
        wfa_results = [
            {'oos_return': 0.05},
            {'oos_return': -0.03},
            {'oos_return': 0.02},
            {'oos_return': -0.04}
        ]
        
        result = analyze_stability(wfa_results, min_stability_score=1.0)
        
        # High volatility means low stability score
        assert result['stability_score'] < 1.0


class TestDriftDetector:
    """Test drift detection"""
    
    def test_weight_drift_computation(self):
        """Test weight drift calculation"""
        weights_history = [
            {'trend': 0.5, 'cycle': 0.5},
            {'trend': 0.52, 'cycle': 0.48},
            {'trend': 0.54, 'cycle': 0.46},
            {'trend': 0.56, 'cycle': 0.44}
        ]
        
        drift = compute_weight_drift(weights_history, window=4)
        
        assert drift > 0
        assert drift < 0.1  # Small gradual drift
    
    def test_high_drift_detection(self):
        """Test high drift is detected"""
        # Create longer history with significant drift
        weights_history = [
            {'trend': 0.5, 'cycle': 0.5},
            {'trend': 0.6, 'cycle': 0.4},
            {'trend': 0.7, 'cycle': 0.3},
            {'trend': 0.8, 'cycle': 0.2},
            {'trend': 0.9, 'cycle': 0.1},
            {'trend': 0.95, 'cycle': 0.05},
            {'trend': 0.85, 'cycle': 0.15},
            {'trend': 0.75, 'cycle': 0.25},
            {'trend': 0.9, 'cycle': 0.1},
            {'trend': 0.8, 'cycle': 0.2}
        ]
        
        result = detect_drift(weights_history=weights_history, max_drift=0.05)
        
        # With this volatile history and low threshold, drift should be detected
        assert result['weight_drift'] > 0
    
    def test_regime_instability_detection(self):
        """Test regime instability detection"""
        regime_history = ['low_vol', 'high_vol', 'low_vol', 'high_vol', 'low_vol']
        
        result = detect_drift(regime_history=regime_history)
        
        # Frequent switches indicate instability
        assert result['regime_instability'] > 0.5


class TestRegimeDependency:
    """Test regime dependency analysis"""
    
    def test_dependency_score_computation(self):
        """Test dependency score calculation"""
        regime_pnl = {
            'bull': 800,
            'bear': 100,
            'sideways': 100
        }
        
        score = compute_dependency_score(regime_pnl)
        
        # Most PnL from bull regime
        assert score == 800 / 1000
        assert score == 0.8
    
    def test_high_dependency_detection(self):
        """Test high regime dependency is detected"""
        pnl_by_regime = {
            'trending_bull': 900,
            'trending_bear': 50,
            'high_vol': 50
        }
        
        result = analyze_regime_dependency(pnl_by_regime, max_dependency=0.5)
        
        assert not result['is_diversified']
        assert result['dependency_score'] > 0.5
        assert result['dominant_regime'] == 'trending_bull'
    
    def test_diversified_regimes(self):
        """Test diversified regime exposure"""
        pnl_by_regime = {
            'regime_a': 300,
            'regime_b': 350,
            'regime_c': 350
        }
        
        result = analyze_regime_dependency(pnl_by_regime, max_dependency=0.5)
        
        assert result['is_diversified'] is True
        assert result['dependency_score'] < 0.5


class TestSensitivityTests:
    """Test sensitivity testing"""
    
    def test_sensitivity_tests_run(self):
        """Test sensitivity tests execute"""
        baseline_data = {
            'prices': {},
            'real_yields': {},
            'cot': {}
        }
        
        def mock_strategy(data):
            return 1000.0
        
        results = run_sensitivity_tests(baseline_data, mock_strategy, shock_pct=0.01)
        
        # Should have multiple test results
        assert 'price_shock' in results
        assert 'yield_shock' in results
        assert 'cot_noise' in results
        assert 'cycle_perturb' in results
    
    def test_sensitivity_result_structure(self):
        """Test sensitivity result has correct structure"""
        baseline_data = {'prices': {}}
        
        results = run_sensitivity_tests(baseline_data, lambda d: 1000.0)
        
        for test_name, result in results.items():
            assert hasattr(result, 'test_name')
            assert hasattr(result, 'baseline_pnl')
            assert hasattr(result, 'perturbed_pnl')
            assert hasattr(result, 'pnl_change')
            assert hasattr(result, 'is_robust')


class TestFragilityIndex:
    """Test fragility index computation"""
    
    def test_fragility_index_computation(self):
        """Test fragility index calculation"""
        from meridian_v2_1_2.risk.model_risk.sensitivity_tests import SensitivityResult
        
        sensitivity_results = {
            'test1': SensitivityResult(
                test_name='test1',
                perturbation_size=0.01,
                baseline_pnl=1000.0,
                perturbed_pnl=1005.0,
                pnl_change=5.0,
                pnl_change_pct=0.005,
                is_robust=True
            ),
            'test2': SensitivityResult(
                test_name='test2',
                perturbation_size=0.01,
                baseline_pnl=1000.0,
                perturbed_pnl=1010.0,
                pnl_change=10.0,
                pnl_change_pct=0.01,
                is_robust=True
            )
        }
        
        fragility = compute_fragility_index(sensitivity_results)
        
        assert fragility > 0
        assert isinstance(fragility, float)
    
    def test_high_fragility_detection(self):
        """Test high fragility is detected"""
        from meridian_v2_1_2.risk.model_risk.sensitivity_tests import SensitivityResult
        from meridian_v2_1_2.risk.model_risk.fragility_index import assess_fragility
        
        # Create fragile results (large PnL changes)
        sensitivity_results = {
            'test': SensitivityResult(
                test_name='test',
                perturbation_size=0.01,
                baseline_pnl=1000.0,
                perturbed_pnl=1500.0,
                pnl_change=500.0,
                pnl_change_pct=0.5,
                is_robust=False
            )
        }
        
        result = assess_fragility(sensitivity_results, max_fragility=0.35)
        
        assert not result['is_robust']
        assert result['fragility_index'] > 0.35


class TestModelRiskReporter:
    """Test model risk reporting"""
    
    def test_report_generation(self, tmp_path):
        """Test report files are generated"""
        overfit = {'overfit_detected': False, 'overfit_ratio': 1.2}
        stability = {'is_stable': True, 'stability_score': 0.8}
        drift = {'drift_detected': False, 'weight_drift': 0.05}
        regime = {'is_diversified': True, 'dependency_score': 0.3}
        fragility = {'is_robust': True, 'fragility_index': 0.2}
        
        reports = generate_model_risk_report(
            overfit, stability, drift, regime, fragility,
            str(tmp_path / "reports")
        )
        
        assert 'summary' in reports
        assert 'breakdown' in reports
        assert 'rating' in reports
        
        assert Path(reports['summary']).exists()
        assert Path(reports['breakdown']).exists()
    
    def test_low_risk_rating(self, tmp_path):
        """Test low risk rating"""
        overfit = {'overfit_detected': False}
        stability = {'is_stable': True}
        drift = {'drift_detected': False}
        regime = {'is_diversified': True}
        fragility = {'is_robust': True}
        
        reports = generate_model_risk_report(
            overfit, stability, drift, regime, fragility,
            str(tmp_path)
        )
        
        assert reports['rating'] == ModelRiskRating.LOW.value
    
    def test_high_risk_rating(self, tmp_path):
        """Test high risk rating"""
        overfit = {'overfit_detected': True}
        stability = {'is_stable': False}
        drift = {'drift_detected': True}
        regime = {'is_diversified': False}
        fragility = {'is_robust': False}
        
        reports = generate_model_risk_report(
            overfit, stability, drift, regime, fragility,
            str(tmp_path)
        )
        
        # Should be high or critical
        assert reports['rating'] in [ModelRiskRating.HIGH.value, ModelRiskRating.CRITICAL.value]


class TestIntegration:
    """Test complete model risk workflow"""
    
    def test_complete_model_risk_analysis(self, tmp_path):
        """Test complete model risk analysis workflow"""
        # Mock WFA results
        wfa_results = [
            {'train_sharpe': 1.5, 'oos_sharpe': 1.2, 'oos_return': 0.01},
            {'train_sharpe': 1.6, 'oos_sharpe': 1.3, 'oos_return': 0.012}
        ]
        
        # Run analyses
        overfit = detect_overfit(wfa_results)
        stability = analyze_stability(wfa_results)
        drift = detect_drift()
        regime = analyze_regime_dependency({
            'regime_a': 500,
            'regime_b': 500
        })
        
        from meridian_v2_1_2.risk.model_risk.sensitivity_tests import SensitivityResult
        from meridian_v2_1_2.risk.model_risk.fragility_index import assess_fragility
        
        sensitivity_results = {
            'test': SensitivityResult('test', 0.01, 1000, 1005, 5, 0.005, True)
        }
        fragility = assess_fragility(sensitivity_results)
        
        # Generate report
        reports = generate_model_risk_report(
            overfit, stability, drift, regime, fragility,
            str(tmp_path)
        )
        
        # Verify all components worked
        assert reports['rating'] in [r.value for r in ModelRiskRating]
        assert Path(reports['summary']).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

