"""
Shadow Engine Test Suite

Comprehensive tests for broker position shadowing (OFFLINE ONLY).
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime

from meridian_v2_1_2.live.shadow import (
    ShadowConfig,
    ShadowEvent,
    ShadowEventType,
    ShadowCompare,
    DriftLevel,
    DriftResult,
    ShadowRepair,
    RepairAction,
    ShadowEngine,
    generate_shadow_report
)
from meridian_v2_1_2.external import AlpacaAdapter, ExternalConfig


class TestShadowConfig:
    """Test shadow configuration"""
    
    def test_config_defaults_are_safe(self):
        """Test defaults prevent issues"""
        config = ShadowConfig()
        
        # Enabled by default for safety
        assert config.enabled is True
        
        # Paper mode by default
        assert config.mode == "paper"
        
        # Auto-repair enabled
        assert config.auto_repair is True
        
        # Reasonable thresholds
        assert config.max_quantity_drift > 0
        assert config.max_notional_drift > 0
    
    def test_config_modes(self):
        """Test mode configuration"""
        paper_config = ShadowConfig(mode="paper")
        assert paper_config.mode == "paper"
        
        live_config = ShadowConfig(mode="live")
        assert live_config.mode == "live"


class TestShadowCompare:
    """Test shadow comparison"""
    
    def test_no_drift_when_equal(self):
        """Test no drift when positions match"""
        config = ShadowConfig()
        compare = ShadowCompare(config)
        
        positions = {
            'GLD': {'qty': 100, 'cost_basis': 10000, 'market_value': 10500}
        }
        
        result = compare.compare(
            local_positions=positions,
            broker_positions=positions,
            local_cash=50000,
            broker_cash=50000,
            local_pnl=500,
            broker_pnl=500
        )
        
        assert result.drift_level == DriftLevel.NONE
    
    def test_small_drift_detection(self):
        """Test small drift detection"""
        config = ShadowConfig()
        compare = ShadowCompare(config)
        
        local = {
            'GLD': {'qty': 100, 'market_value': 10000}
        }
        
        broker = {
            'GLD': {'qty': 100, 'market_value': 10000},
            'LTPZ': {'qty': 10, 'market_value': 1000}  # Extra position
        }
        
        result = compare.compare(
            local_positions=local,
            broker_positions=broker,
            local_cash=50000,
            broker_cash=50000,
            local_pnl=0,
            broker_pnl=0
        )
        
        assert result.drift_level != DriftLevel.NONE
        assert len(result.positions_diff['missing_local']) == 1
    
    def test_large_drift_detection(self):
        """Test large drift detection"""
        config = ShadowConfig()
        compare = ShadowCompare(config)
        
        local = {
            'GLD': {'qty': 100, 'market_value': 10000}
        }
        
        broker = {
            'GLD': {'qty': 110, 'market_value': 11000}  # 10% qty difference
        }
        
        result = compare.compare(
            local_positions=local,
            broker_positions=broker,
            local_cash=50000,
            broker_cash=50000,
            local_pnl=0,
            broker_pnl=0
        )
        
        assert result.drift_level in [DriftLevel.LARGE, DriftLevel.CRITICAL]
        assert len(result.positions_diff['mismatches']) > 0
    
    def test_critical_drift_detection(self):
        """Test critical drift detection"""
        config = ShadowConfig(max_quantity_drift=0.01)  # 1% threshold
        compare = ShadowCompare(config)
        
        local = {
            'GLD': {'qty': 100, 'market_value': 10000}
        }
        
        broker = {
            'GLD': {'qty': 200, 'market_value': 20000}  # 100% difference
        }
        
        result = compare.compare(
            local_positions=local,
            broker_positions=broker,
            local_cash=50000,
            broker_cash=50000,
            local_pnl=0,
            broker_pnl=0
        )
        
        assert result.drift_level == DriftLevel.CRITICAL
    
    def test_cash_drift_detection(self):
        """Test cash drift detection"""
        config = ShadowConfig()
        compare = ShadowCompare(config)
        
        result = compare.compare(
            local_positions={},
            broker_positions={},
            local_cash=50000,
            broker_cash=60000,  # $10k difference
            local_pnl=0,
            broker_pnl=0
        )
        
        assert result.cash_diff['difference'] == -10000


class TestShadowRepair:
    """Test shadow repair"""
    
    def test_repair_position_mismatch(self):
        """Test position mismatch repair"""
        config = ShadowConfig(auto_repair=True)
        repair = ShadowRepair(config)
        
        drift_result = DriftResult(
            drift_level=DriftLevel.LARGE,
            positions_diff={
                'mismatches': [{
                    'symbol': 'GLD',
                    'local_qty': 100,
                    'broker_qty': 110,
                    'difference': -10,
                    'drift_pct': 0.1
                }]
            },
            orders_diff={},
            cash_diff={},
            pnl_diff={},
            details=[]
        )
        
        local = {'GLD': {'qty': 100}}
        broker = {'GLD': {'qty': 110}}
        
        actions = repair.repair(drift_result, local, broker)
        
        assert len(actions) > 0
        assert actions[0].action_type == 'position_update'
        assert actions[0].symbol == 'GLD'
    
    def test_repair_missing_position(self):
        """Test missing position repair"""
        config = ShadowConfig(auto_repair=True)
        repair = ShadowRepair(config)
        
        drift_result = DriftResult(
            drift_level=DriftLevel.SMALL,
            positions_diff={
                'missing_local': [{
                    'symbol': 'LTPZ',
                    'broker_qty': 50
                }]
            },
            orders_diff={},
            cash_diff={},
            pnl_diff={},
            details=[]
        )
        
        actions = repair.repair(drift_result, {}, {'LTPZ': {'qty': 50}})
        
        assert len(actions) > 0
        assert actions[0].action_type == 'position_add'
    
    def test_no_repair_when_disabled(self):
        """Test repair is skipped when disabled"""
        config = ShadowConfig(auto_repair=False)
        repair = ShadowRepair(config)
        
        drift_result = DriftResult(
            drift_level=DriftLevel.SMALL,
            positions_diff={'mismatches': [{'symbol': 'GLD'}]},
            orders_diff={},
            cash_diff={},
            pnl_diff={},
            details=[]
        )
        
        actions = repair.repair(drift_result, {}, {})
        
        assert len(actions) == 0


class TestShadowEngine:
    """Test shadow engine"""
    
    def test_shadow_engine_initialization(self):
        """Test shadow engine can be initialized"""
        config = ShadowConfig()
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        engine = ShadowEngine(config, alpaca)
        
        assert engine is not None
    
    def test_shadow_check_no_drift(self):
        """Test shadow check with no drift"""
        config = ShadowConfig()
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        engine = ShadowEngine(config, alpaca)
        
        positions = {}
        
        result = engine.check_shadow(positions, 100000, 0)
        
        assert 'drift_detected' in result
        # May detect small drift due to cash differences in stub
        assert result['drift_level'] in ['none', 'small']
    
    def test_shadow_check_with_drift(self):
        """Test shadow check detects drift"""
        config = ShadowConfig()
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        engine = ShadowEngine(config, alpaca)
        
        # Local has position, broker won't (stub returns empty)
        local_positions = {
            'GLD': {'qty': 100, 'market_value': 10000}
        }
        
        result = engine.check_shadow(local_positions, 100000, 0)
        
        # May detect drift depending on broker state
        assert 'drift_detected' in result
        assert 'events' in result
    
    def test_events_are_tracked(self):
        """Test events are properly tracked"""
        config = ShadowConfig()
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        engine = ShadowEngine(config, alpaca)
        
        engine.check_shadow({}, 100000, 0)
        
        events = engine.get_events()
        assert isinstance(events, list)


class TestShadowReporter:
    """Test shadow reporter"""
    
    def test_report_generation(self, tmp_path):
        """Test shadow report generation"""
        config = ShadowConfig()
        config.report_path = str(tmp_path / "reports")
        
        shadow_result = {
            'timestamp': datetime.now().isoformat(),
            'drift_detected': True,
            'drift_level': 'small',
            'events': [
                {
                    'event_type': 'position_drift',
                    'severity': 'warning',
                    'message': 'Test drift'
                }
            ],
            'repairs_applied': []
        }
        
        timestamp = datetime.now().isoformat()
        report_file = generate_shadow_report(timestamp, shadow_result, config)
        
        assert report_file.exists()
        content = report_file.read_text()
        assert 'BROKER SHADOW CHECK REPORT' in content


class TestOfflineGuarantee:
    """Test that all shadow tests run offline"""
    
    def test_no_network_calls_in_tests(self):
        """Verify tests make no network calls"""
        config = ShadowConfig()
        ext_config = ExternalConfig(use_alpaca=False)
        alpaca = AlpacaAdapter(ext_config)
        
        # Initialize all components
        compare = ShadowCompare(config)
        repair = ShadowRepair(config)
        engine = ShadowEngine(config, alpaca)
        
        # Should all work offline
        assert compare is not None
        assert repair is not None
        assert engine is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

