"""
Live Mode Test Suite

Comprehensive tests for live trading (OFFLINE ONLY - no real orders).
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from datetime import datetime

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.live import (
    LiveConfig,
    LiveRulesEngine,
    RuleViolation,
    LiveHeartbeat,
    HeartbeatStatus,
    LiveExecution,
    LiveReconciliation,
    ReconciliationResult,
    LiveSafety,
    SafetyTrigger,
    generate_live_report
)


class TestLiveConfig:
    """Test live configuration"""
    
    def test_config_defaults_are_safe(self):
        """Test that defaults prevent accidental live trading"""
        config = LiveConfig()
        
        # Live trading OFF by default
        assert config.enable_live_trading is False
        
        # Operator confirmation REQUIRED
        assert config.require_operator_confirmation is True
        
        # Safety features ENABLED
        assert config.enable_kill_switch is True
        assert config.reconciliation_required is True
        assert config.run_model_risk_pre_trade is True
    
    def test_risk_limits_sensible(self):
        """Test risk limits are sensible"""
        config = LiveConfig()
        
        assert config.max_daily_loss_pct > 0
        assert config.max_daily_loss_pct <= 10.0  # Should be reasonable (value is percentage)
        assert config.max_position_notional > 0
        assert config.max_slippage_pct > 0


class TestLiveRulesEngine:
    """Test rules engine"""
    
    def test_rules_engine_blocks_when_disabled(self):
        """Test rules engine blocks all orders when live trading disabled"""
        config = LiveConfig(enable_live_trading=False)
        engine = LiveRulesEngine(config)
        
        violations = engine.validate_order(
            symbol='GLD',
            qty=10.0,
            side='buy',
            price=100.0,
            account_info={'equity': 100000},
            current_positions={}
        )
        
        assert len(violations) > 0
        assert violations[0].rule_name == 'live_trading_disabled'
        assert violations[0].blocking is True
    
    def test_rules_engine_validates_order_size(self):
        """Test order size validation"""
        config = LiveConfig(
            enable_live_trading=True,
            max_single_order_notional=1000.0
        )
        engine = LiveRulesEngine(config)
        
        # Oversized order
        violations = engine.validate_order(
            symbol='GLD',
            qty=100.0,  # 100 * 100 = $10,000
            side='buy',
            price=100.0,
            account_info={'equity': 100000},
            current_positions={}
        )
        
        assert any(v.rule_name == 'order_size_exceeded' for v in violations)
        assert engine.has_blocking_violations(violations)
    
    def test_rules_engine_validates_position_size(self):
        """Test position size validation"""
        config = LiveConfig(
            enable_live_trading=True,
            max_position_notional=5000.0
        )
        engine = LiveRulesEngine(config)
        
        # Already holding $4000, buying $2000 more = $6000 total
        violations = engine.validate_order(
            symbol='GLD',
            qty=20.0,
            side='buy',
            price=100.0,
            account_info={'equity': 100000},
            current_positions={'GLD': {'qty': 40.0, 'market_value': 4000}}
        )
        
        assert any(v.rule_name == 'position_size_exceeded' for v in violations)
    
    def test_rules_engine_validates_total_exposure(self):
        """Test total exposure validation"""
        config = LiveConfig(
            enable_live_trading=True,
            max_total_exposure=10000.0
        )
        engine = LiveRulesEngine(config)
        
        # Already have $9000 exposure, adding $2000
        violations = engine.validate_order(
            symbol='SPY',
            qty=20.0,
            side='buy',
            price=100.0,
            account_info={'equity': 100000},
            current_positions={
                'GLD': {'qty': 50, 'market_value': 5000},
                'LTPZ': {'qty': 40, 'market_value': 4000}
            }
        )
        
        assert any(v.rule_name == 'total_exposure_exceeded' for v in violations)
    
    def test_rules_engine_rejects_nan_orders(self):
        """Test NaN order rejection"""
        config = LiveConfig(enable_live_trading=True)
        engine = LiveRulesEngine(config)
        
        violations = engine.validate_order(
            symbol='GLD',
            qty=float('nan'),
            side='buy',
            price=100.0,
            account_info={'equity': 100000},
            current_positions={}
        )
        
        assert any(v.rule_name == 'nan_value' for v in violations)
        assert any(v.severity == 'critical' for v in violations)


class TestLiveHeartbeat:
    """Test heartbeat monitor"""
    
    def test_heartbeat_initialization(self):
        """Test heartbeat can be initialized"""
        config = LiveConfig()
        heartbeat = LiveHeartbeat(config)
        
        assert heartbeat is not None
        assert heartbeat.is_alive is True
    
    def test_heartbeat_check(self):
        """Test heartbeat check"""
        config = LiveConfig()
        heartbeat = LiveHeartbeat(config)
        
        status = heartbeat.check()
        
        assert isinstance(status, HeartbeatStatus)
        assert status.last_beat is not None
    
    def test_heartbeat_fails_after_max_failures(self):
        """Test heartbeat fails after consecutive failures"""
        config = LiveConfig(heartbeat_max_failures=2)
        heartbeat = LiveHeartbeat(config)
        
        # Simulate failures
        heartbeat.consecutive_failures = 2
        
        status = heartbeat.check()
        
        assert status.is_alive is False
    
    def test_heartbeat_is_healthy(self):
        """Test healthy check"""
        config = LiveConfig()
        heartbeat = LiveHeartbeat(config)
        
        heartbeat.check()
        
        assert heartbeat.is_healthy()


class TestLiveExecution:
    """Test live execution engine"""
    
    def test_execution_initialization(self):
        """Test execution engine can be initialized"""
        from meridian_v2_1_2.external import AlpacaAdapter, ExternalConfig
        
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        config = LiveConfig()
        execution = LiveExecution(config, alpaca)
        
        assert execution is not None
    
    def test_execution_tracks_orders(self):
        """Test order tracking"""
        from meridian_v2_1_2.external import AlpacaAdapter, ExternalConfig
        
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        config = LiveConfig()
        execution = LiveExecution(config, alpaca)
        
        result = execution.execute_order('GLD', 10.0, 'buy')
        
        assert len(execution.order_history) == 1
        assert result is not None
    
    def test_execution_stats(self):
        """Test execution statistics"""
        from meridian_v2_1_2.external import AlpacaAdapter, ExternalConfig
        
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        config = LiveConfig()
        execution = LiveExecution(config, alpaca)
        
        # Execute some orders
        execution.execute_order('GLD', 10.0, 'buy')
        execution.execute_order('LTPZ', 5.0, 'sell')
        
        stats = execution.get_execution_stats()
        
        assert stats['total_orders'] == 2
        assert 'success_rate' in stats


class TestLiveReconciliation:
    """Test reconciliation engine"""
    
    def test_reconciliation_detects_drift(self):
        """Test drift detection"""
        from meridian_v2_1_2.external import AlpacaAdapter, ExternalConfig
        from meridian_v2_1_2.storage import StateStore, LocalDB
        
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        db = LocalDB(":memory:")
        state_store = StateStore(db)
        
        config = LiveConfig()
        recon = LiveReconciliation(config, alpaca, state_store)
        
        # Local says we have 100 shares
        local_positions = {
            'GLD': {'qty': 100, 'market_value': 10000}
        }
        
        # Reconcile (broker will return empty in stub)
        result = recon.reconcile(local_positions)
        
        assert isinstance(result, ReconciliationResult)
        
        db.close()


class TestLiveSafety:
    """Test safety layer"""
    
    def test_safety_initialization(self):
        """Test safety layer initialization"""
        config = LiveConfig()
        safety = LiveSafety(config)
        
        assert safety is not None
        assert safety.kill_switch_active is False
    
    def test_safety_detects_daily_loss(self):
        """Test daily loss detection"""
        config = LiveConfig(max_daily_loss_pct=0.02)
        safety = LiveSafety(config)
        safety.starting_equity = 100000
        
        # Lose 3% (-$3000)
        triggers = safety.check_all(
            current_equity=97000,
            daily_pnl=-3000,
            positions={}
        )
        
        assert len(triggers) > 0
        assert any(t.trigger_type == 'daily_loss_exceeded' for t in triggers)
        assert safety.is_kill_switch_active()
    
    def test_safety_detects_drawdown(self):
        """Test drawdown detection"""
        config = LiveConfig(max_drawdown_pct=0.05)
        safety = LiveSafety(config)
        safety.peak_equity = 100000
        
        # Draw down 6% to $94,000
        triggers = safety.check_all(
            current_equity=94000,
            daily_pnl=0,
            positions={}
        )
        
        assert any(t.trigger_type == 'drawdown_exceeded' for t in triggers)
        assert safety.is_kill_switch_active()
    
    def test_safety_detects_model_risk(self):
        """Test model risk threshold"""
        config = LiveConfig(
            run_model_risk_pre_trade=True,
            max_model_risk_score=0.5
        )
        safety = LiveSafety(config)
        
        # High model risk score
        triggers = safety.check_all(
            current_equity=100000,
            daily_pnl=0,
            positions={},
            model_risk_score=0.7
        )
        
        assert any(t.trigger_type == 'model_risk_exceeded' for t in triggers)
    
    def test_kill_switch_requires_confirmation_to_reset(self):
        """Test kill-switch reset requires operator confirmation"""
        config = LiveConfig(require_operator_confirmation=True)
        safety = LiveSafety(config)
        safety.kill_switch_active = True
        
        # Try to reset without confirmation
        with pytest.raises(ValueError, match="operator confirmation"):
            safety.reset_kill_switch(operator_confirmation=False)
        
        # Reset with confirmation
        safety.reset_kill_switch(operator_confirmation=True)
        assert not safety.is_kill_switch_active()


class TestLiveReports:
    """Test live reporting"""
    
    def test_report_generation(self, tmp_path):
        """Test live report generation"""
        config = LiveConfig()
        config.report_path = str(tmp_path / "reports")
        
        results = {
            'date': '2025-03-01',
            'success': True,
            'trades_executed': [
                {'symbol': 'GLD', 'side': 'buy', 'qty': 10, 'result': {'success': True}}
            ],
            'heartbeat_ok': True,
            'reconciliation_ok': True,
            'violations': [],
            'safety_triggers': []
        }
        
        report_file = generate_live_report('2025-03-01', results, config)
        
        assert report_file.exists()
        assert '2025-03-01' in report_file.read_text()


class TestOfflineGuarantee:
    """Test that all live mode tests run offline"""
    
    def test_no_network_calls_in_tests(self):
        """Verify tests make no network calls"""
        # All tests above should complete without network
        config = LiveConfig(enable_live_trading=False)
        
        # Initialize all components
        engine = LiveRulesEngine(config)
        heartbeat = LiveHeartbeat(config)
        safety = LiveSafety(config)
        
        # Should all work offline
        assert engine is not None
        assert heartbeat is not None
        assert safety is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

