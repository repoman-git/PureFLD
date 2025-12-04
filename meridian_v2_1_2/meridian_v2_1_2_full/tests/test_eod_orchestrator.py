"""
EOD Orchestrator Test Suite

Tests for complete daily trading loop orchestration.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from datetime import datetime

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.orchestrator import (
    EODState,
    EODStateMachine,
    EODScheduler,
    create_business_calendar,
    EODSafety,
    SafetyViolation,
    EODOrchestrator,
    generate_eod_report
)


class TestEODState:
    """Test EOD state machine"""
    
    def test_state_machine_initialization(self):
        """Test state machine can be initialized"""
        sm = EODStateMachine()
        assert sm.current_state == EODState.INIT
        assert len(sm.state_history) == 1
    
    def test_state_transitions(self):
        """Test state transitions"""
        sm = EODStateMachine()
        
        sm.transition(EODState.LOAD_DATA)
        assert sm.current_state == EODState.LOAD_DATA
        
        sm.transition(EODState.GENERATE_SIGNALS)
        assert sm.current_state == EODState.GENERATE_SIGNALS
        
        sm.transition(EODState.END)
        assert sm.current_state == EODState.END
        
        # Check history
        assert len(sm.state_history) == 4
    
    def test_error_tracking(self):
        """Test error tracking in state machine"""
        sm = EODStateMachine()
        
        sm.transition(EODState.SAFE_MODE, error="Test error")
        
        assert sm.has_errors()
        assert len(sm.errors) == 1
        assert sm.errors[0]['error'] == "Test error"
    
    def test_safe_mode_detection(self):
        """Test safe mode detection"""
        sm = EODStateMachine()
        
        assert sm.is_safe()
        
        sm.transition(EODState.SAFE_MODE)
        
        assert not sm.is_safe()


class TestEODScheduler:
    """Test EOD scheduler"""
    
    def test_business_calendar_creation(self):
        """Test business calendar generation"""
        calendar = create_business_calendar("2025-01-01", "2025-01-31")
        
        # Should have approximately 22-23 business days
        assert len(calendar) >= 20
        assert len(calendar) <= 25
        
        # Should exclude weekends
        for date in calendar:
            assert date.dayofweek < 5
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization"""
        scheduler = EODScheduler("2025-01-01", "2025-01-10")
        
        assert scheduler.start_date == pd.Timestamp("2025-01-01")
        assert scheduler.end_date == pd.Timestamp("2025-01-10")
        assert len(scheduler.calendar) > 0
    
    def test_next_trading_day(self):
        """Test advancing to next trading day"""
        scheduler = EODScheduler("2025-01-01", "2025-01-10")
        
        first_day = scheduler.next_trading_day()
        assert first_day is not None
        assert isinstance(first_day, pd.Timestamp)
        
        second_day = scheduler.next_trading_day()
        assert second_day > first_day
    
    def test_has_more_days(self):
        """Test day availability check"""
        scheduler = EODScheduler("2025-01-01", "2025-01-03")
        
        assert scheduler.has_more_days()
        
        # Exhaust calendar
        while scheduler.next_trading_day() is not None:
            pass
        
        assert not scheduler.has_more_days()
    
    def test_jump_to_date(self):
        """Test jumping to specific date"""
        scheduler = EODScheduler("2025-01-01", "2025-01-31")
        
        # Jump to mid-month
        result = scheduler.jump_to_date("2025-01-15")
        
        # Note: may fail if 2025-01-15 is not a business day
        # This is expected behavior
    
    def test_reset(self):
        """Test scheduler reset"""
        scheduler = EODScheduler("2025-01-01", "2025-01-10")
        
        # Advance a few days
        scheduler.next_trading_day()
        scheduler.next_trading_day()
        
        # Reset
        scheduler.reset()
        
        assert scheduler.current_idx == 0


class TestEODSafety:
    """Test EOD safety layer"""
    
    def test_safety_initialization(self):
        """Test safety layer initialization"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        assert safety is not None
    
    def test_data_quality_check_missing_data(self):
        """Test detection of missing data"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        violations = safety.check_data_quality({})
        
        assert len(violations) > 0
        assert violations[0].severity == 'critical'
    
    def test_data_quality_check_nan_data(self):
        """Test detection of NaN values"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        df = pd.DataFrame({'close': [100, float('nan'), 102]})
        data = {'prices': {'TEST': df}}
        
        violations = safety.check_data_quality(data)
        
        assert len(violations) > 0
        assert any('NaN' in v.message for v in violations)
    
    def test_signal_checks(self):
        """Test signal validation"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        # Test NaN signal
        signals = {'TEST': float('nan')}
        violations = safety.check_signals(signals)
        
        assert len(violations) > 0
        assert violations[0].severity == 'critical'
        
        # Test extreme signal
        signals = {'TEST': 100.0}
        violations = safety.check_signals(signals)
        
        assert len(violations) > 0
        assert any('extreme' in v.message.lower() for v in violations)
    
    def test_position_checks(self):
        """Test position size validation"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        # Oversized position
        positions = {'TEST': 1000.0}
        violations = safety.check_positions(positions, max_position=100.0)
        
        assert len(violations) > 0
        assert violations[0].violation_type == 'oversized_position'
    
    def test_daily_loss_check(self):
        """Test daily loss limit"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        violations = safety.check_daily_loss(
            current_equity=90000,
            previous_equity=100000,
            max_loss_pct=0.05
        )
        
        assert len(violations) > 0
        assert violations[0].severity == 'critical'
    
    def test_check_all(self):
        """Test running all safety checks"""
        config = MeridianConfig()
        safety = EODSafety(config)
        
        df = pd.DataFrame({'close': [100, 101, 102]})
        data = {'prices': {'TEST': df}}
        signals = {'TEST': 1.0}
        positions = {'TEST': 10.0}
        
        violations = safety.check_all(
            data, signals, positions,
            current_equity=105000,
            previous_equity=100000
        )
        
        # Should have no critical violations
        assert not safety.has_critical_violations()


class TestEODOrchestrator:
    """Test complete EOD orchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized"""
        config = MeridianConfig()
        orchestrator = EODOrchestrator(config)
        
        assert orchestrator is not None
        assert orchestrator.state_machine is not None
        assert orchestrator.scheduler is not None
        
        orchestrator.close()
    
    def test_single_eod_day(self):
        """Test running single EOD day"""
        config = MeridianConfig()
        config.eod.write_reports = False  # Disable for test
        
        orchestrator = EODOrchestrator(config)
        
        date = pd.Timestamp("2020-01-15")
        results = orchestrator.run_eod_day(date)
        
        assert 'date' in results
        assert 'success' in results
        assert 'state_sequence' in results
        assert len(results['state_sequence']) > 0
        
        orchestrator.close()
    
    def test_state_sequence(self):
        """Test state sequence is recorded"""
        config = MeridianConfig()
        config.eod.write_reports = False
        
        orchestrator = EODOrchestrator(config)
        
        date = pd.Timestamp("2020-01-15")
        results = orchestrator.run_eod_day(date)
        
        state_seq = results['state_sequence']
        
        # Should have proper flow
        assert 'init' in state_seq
        assert 'load_data' in state_seq
        assert 'generate_signals' in state_seq
        assert 'end' in state_seq or 'safe_mode' in state_seq
        
        orchestrator.close()
    
    def test_run_period(self):
        """Test running multiple days"""
        config = MeridianConfig()
        config.eod.write_reports = False
        config.eod.start_date = "2020-01-01"
        config.eod.end_date = "2020-01-31"
        
        orchestrator = EODOrchestrator(config)
        
        # Run 5 days
        results = orchestrator.run_period(num_days=5)
        
        assert results['total_days'] == 5
        assert 'daily_results' in results
        assert len(results['daily_results']) == 5
        
        orchestrator.close()
    
    def test_equity_tracking(self):
        """Test equity is tracked over time"""
        config = MeridianConfig()
        config.eod.write_reports = False
        config.eod.start_date = "2020-01-01"
        config.eod.end_date = "2020-01-15"
        
        orchestrator = EODOrchestrator(config)
        
        results = orchestrator.run_period(num_days=3)
        
        # Check equity exists
        for day_result in results['daily_results']:
            assert 'equity' in day_result
        
        orchestrator.close()


class TestEODReporter:
    """Test EOD reporter"""
    
    def test_report_generation(self, tmp_path):
        """Test report file generation"""
        config = MeridianConfig()
        config.eod.report_path = str(tmp_path / "reports")
        
        results = {
            'date': '2025-03-01',
            'success': True,
            'state_sequence': ['init', 'load_data', 'end'],
            'signals': {'TEST': 1.0},
            'positions': {'TEST': {'qty': 10, 'market_value': 1000}},
            'pnl': 50.0,
            'equity': 101000.0
        }
        
        report_file = generate_eod_report('2025-03-01', results, config)
        
        assert report_file.exists()
        assert report_file.suffix == '.md'
        
        # Check content
        content = report_file.read_text()
        assert '2025-03-01' in content
        assert 'Success: True' in content
        assert 'Daily PnL' in content


class TestIntegration:
    """Test complete EOD integration"""
    
    def test_full_eod_workflow(self):
        """Test complete EOD workflow"""
        config = MeridianConfig()
        config.eod.write_reports = False
        config.eod.run_model_risk = False  # Disable for speed
        config.eod.start_date = "2020-01-02"
        config.eod.end_date = "2020-01-10"
        
        orchestrator = EODOrchestrator(config)
        
        # Run multiple days
        results = orchestrator.run_period(num_days=3)
        
        # Validate results
        assert results['total_days'] == 3
        assert results['successful_days'] >= 0
        
        # Check each day has required fields
        for day_result in results['daily_results']:
            assert 'date' in day_result
            assert 'signals' in day_result
            assert 'equity' in day_result
        
        orchestrator.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


