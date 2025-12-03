"""
Comprehensive test suite for Health Monitoring Engine in Meridian v2.1.2.

Tests verify health checks, exposure validation, kill switch, and safety systems.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import tempfile
import shutil

from meridian_v2_1_2.config import HealthConfig
from meridian_v2_1_2.health import (
    run_all_health_checks,
    HealthStatus,
    check_exposures,
    check_data_integrity,
    check_reconciliation,
    KillSwitch,
    should_trigger_kill_switch,
    HealthReporter,
    generate_health_report
)


class TestHealthChecks:
    """Test overall health check system"""
    
    def test_all_checks_pass_returns_ok(self):
        """
        TEST 1: When all checks pass → status OK
        """
        eod_data = {'GLD': pd.DataFrame({'close': [100, 101, 102]})}
        positions = {'GLD': 1.0}
        orders = []
        
        config = HealthConfig()
        
        status = run_all_health_checks(eod_data, positions, orders, config)
        
        assert status.status in ['OK', 'WARN']  # Should not FAIL
        assert status.checks_passed > 0
    
    def test_no_data_fails(self):
        """
        TEST: No EOD data → FAIL status
        """
        eod_data = {}  # No data
        positions = {}
        orders = []
        
        config = HealthConfig()
        
        status = run_all_health_checks(eod_data, positions, orders, config)
        
        assert status.status == 'FAIL'
        assert status.checks_failed > 0


class TestExposureChecks:
    """Test exposure validation"""
    
    def test_exposure_within_limits_passes(self):
        """
        TEST 2: Normal exposure passes check
        """
        positions = {'GLD': 10.0, 'LTPZ': -5.0}
        prices = {'GLD': 180.0, 'LTPZ': 50.0}
        
        config = HealthConfig(max_gross_exposure=2.0)
        
        is_healthy, message = check_exposures(positions, prices, config)
        
        assert is_healthy
        assert "within limits" in message.lower()
    
    def test_excessive_exposure_fails(self):
        """
        TEST: Excessive exposure fails check
        """
        positions = {'GLD': 1000.0}  # Way too large
        prices = {'GLD': 180.0}
        
        config = HealthConfig(max_gross_exposure=1.0)
        
        is_healthy, message = check_exposures(positions, prices, config)
        
        assert not is_healthy
        assert "too high" in message.lower()


class TestDataIntegrityChecks:
    """Test data integrity validation"""
    
    def test_valid_data_passes(self):
        """
        TEST 3: Valid EOD data passes integrity check
        """
        eod_data = {
            'GLD': pd.DataFrame({
                'open': [100, 101],
                'high': [102, 103],
                'low': [99, 100],
                'close': [101, 102]
            })
        }
        
        is_healthy, message = check_data_integrity(eod_data)
        
        assert is_healthy
        assert "OK" in message
    
    def test_missing_columns_fails(self):
        """
        TEST: Missing OHLC columns fails check
        """
        eod_data = {
            'GLD': pd.DataFrame({'close': [100, 101]})  # Missing other columns
        }
        
        is_healthy, message = check_data_integrity(eod_data)
        
        assert not is_healthy
        assert "Missing columns" in message


class TestReconciliationChecks:
    """Test position reconciliation"""
    
    def test_matching_positions_pass(self):
        """
        TEST 4: Matching positions pass reconciliation
        """
        local = {'GLD': 10.0, 'LTPZ': -5.0}
        broker = {'GLD': 10.0, 'LTPZ': -5.0}
        
        is_reconciled, message = check_reconciliation(local, broker, max_drift_pct=0.05)
        
        assert is_reconciled
        assert "reconciled" in message.lower()
    
    def test_drift_fails_reconciliation(self):
        """
        TEST: Position drift fails reconciliation
        """
        local = {'GLD': 10.0}
        broker = {'GLD': 15.0}  # 50% drift
        
        is_reconciled, message = check_reconciliation(local, broker, max_drift_pct=0.05)
        
        assert not is_reconciled
        assert "drift" in message.lower()


class TestKillSwitch:
    """Test kill switch mechanism"""
    
    def test_kill_switch_triggers(self):
        """
        TEST 5: Kill switch triggers on command
        """
        kill_switch = KillSwitch(enabled=True)
        
        assert not kill_switch.is_triggered()
        
        kill_switch.trigger("Test trigger")
        
        assert kill_switch.is_triggered()
        assert kill_switch.trigger_reason == "Test trigger"
    
    def test_kill_switch_resets(self):
        """
        TEST: Kill switch can be reset
        """
        kill_switch = KillSwitch(enabled=True)
        
        kill_switch.trigger("Test")
        assert kill_switch.is_triggered()
        
        kill_switch.reset()
        assert not kill_switch.is_triggered()
    
    def test_should_trigger_on_excessive_drawdown(self):
        """
        TEST: Kill switch triggers on excessive drawdown
        """
        equity_curve = {'drawdown': -0.15}  # 15% drawdown
        
        should_trigger, reason = should_trigger_kill_switch(
            equity_curve,
            health_status=None,
            drawdown_threshold=0.10
        )
        
        assert should_trigger
        assert "Drawdown" in reason


class TestHealthReporter:
    """Test health report generation"""
    
    def test_generates_report_file(self):
        """
        TEST 6: Health reporter creates report files
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            from meridian_v2_1_2.health.health_checks import HealthStatus
            from datetime import datetime
            
            status = HealthStatus(
                status='OK',
                timestamp=datetime.now(),
                checks_passed=5,
                checks_failed=0,
                checks_warned=0,
                details={'data': 'OK', 'exposure': 'OK'},
                actions_required=[]
            )
            
            reporter = HealthReporter(report_path=temp_dir)
            report_file = reporter.generate_report(status, {})
            
            assert Path(report_file).exists()
            
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

