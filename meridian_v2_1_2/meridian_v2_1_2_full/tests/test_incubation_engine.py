"""
Test suite for Incubation Platform

Tests strategy lifecycle management: Research → WFA → Paper → Live
"""

import pytest
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.incubation import (
    StrategyState,
    StrategyStatus,
    load_strategy_state,
    save_strategy_state,
    evaluate_promotion,
    can_promote_to_paper,
    can_promote_to_live,
    evaluate_demotion,
    should_demote_to_disabled,
    run_incubation_cycle,
    update_strategy_state,
    generate_incubation_report
)
from meridian_v2_1_2.config import MeridianConfig


class TestStrategyStateMachine:
    """Test strategy state persistence"""
    
    def test_strategy_status_creation(self):
        """Test creating a strategy status"""
        status = StrategyStatus(
            strategy_name="test_strategy",
            state=StrategyState.RESEARCH
        )
        
        assert status.strategy_name == "test_strategy"
        assert status.state == StrategyState.RESEARCH
        assert status.days_in_state == 0
    
    def test_status_to_dict(self):
        """Test serialization"""
        status = StrategyStatus(
            strategy_name="test_strategy",
            state=StrategyState.PAPER_TRADING,
            days_in_state=15
        )
        
        data = status.to_dict()
        
        assert data['strategy_name'] == "test_strategy"
        assert data['state'] == "paper_trading"
        assert data['days_in_state'] == 15
    
    def test_status_from_dict(self):
        """Test deserialization"""
        data = {
            'strategy_name': 'test',
            'state': 'live_trading',
            'days_in_state': 100,
            'version': 'v2.1.2'
        }
        
        status = StrategyStatus.from_dict(data)
        
        assert status.strategy_name == 'test'
        assert status.state == StrategyState.LIVE_TRADING
        assert status.days_in_state == 100
    
    def test_save_and_load_state(self, tmp_path):
        """Test saving and loading state"""
        state_file = tmp_path / "test_state.json"
        
        status = StrategyStatus(
            strategy_name="test_strategy",
            state=StrategyState.PAPER_TRADING,
            days_in_state=25
        )
        
        save_strategy_state(status, str(state_file))
        
        # Load it back
        loaded = load_strategy_state("test_strategy", str(state_file))
        
        assert loaded.strategy_name == "test_strategy"
        assert loaded.state == StrategyState.PAPER_TRADING
        assert loaded.days_in_state == 25
    
    def test_load_nonexistent_strategy(self, tmp_path):
        """Test loading a strategy that doesn't exist"""
        state_file = tmp_path / "empty_state.json"
        
        status = load_strategy_state("new_strategy", str(state_file))
        
        # Should get default state
        assert status.strategy_name == "new_strategy"
        assert status.state == StrategyState.RESEARCH


class TestPromotionRules:
    """Test promotion criteria"""
    
    def test_can_promote_to_paper_success(self):
        """Test successful WFA → Paper promotion"""
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        can_promote, reason = can_promote_to_paper(wfa_metrics, cfg)
        
        assert can_promote is True
        assert "criteria met" in reason.lower()
    
    def test_can_promote_to_paper_low_sharpe(self):
        """Test promotion blocked by low Sharpe"""
        wfa_metrics = {
            'mean_oos_sharpe': 0.5,  # Too low
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        can_promote, reason = can_promote_to_paper(wfa_metrics, cfg)
        
        assert can_promote is False
        assert "sharpe" in reason.lower()
    
    def test_can_promote_to_paper_overfit(self):
        """Test promotion blocked by overfitting"""
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 3.5,  # Overfitting
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        can_promote, reason = can_promote_to_paper(wfa_metrics, cfg)
        
        assert can_promote is False
        assert "overfit" in reason.lower()
    
    def test_can_promote_to_live_success(self):
        """Test successful Paper → Live promotion"""
        paper_metrics = {
            'sharpe': 1.0,
            'max_drawdown': 0.08
        }
        
        cfg = MeridianConfig()
        cfg.incubation.require_manual_live_approval = False
        
        can_promote, reason = can_promote_to_live(paper_metrics, 50, cfg)
        
        assert can_promote is True
    
    def test_can_promote_to_live_insufficient_days(self):
        """Test promotion blocked by insufficient days"""
        paper_metrics = {
            'sharpe': 1.0,
            'max_drawdown': 0.08
        }
        
        cfg = MeridianConfig()
        
        can_promote, reason = can_promote_to_live(paper_metrics, 20, cfg)
        
        assert can_promote is False
        assert "days" in reason.lower()
    
    def test_can_promote_to_live_manual_approval(self):
        """Test manual approval requirement"""
        paper_metrics = {
            'sharpe': 1.0,
            'max_drawdown': 0.08
        }
        
        cfg = MeridianConfig()
        cfg.incubation.require_manual_live_approval = True
        
        can_promote, reason = can_promote_to_live(paper_metrics, 50, cfg)
        
        assert can_promote is False
        assert "manual" in reason.lower()
    
    def test_evaluate_promotion_wfa_to_paper(self):
        """Test promotion evaluation from WFA to Paper"""
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        new_state, reason = evaluate_promotion(
            StrategyState.WFA_PASSED,
            wfa_metrics,
            {},
            0,
            cfg
        )
        
        assert new_state == StrategyState.PAPER_TRADING


class TestDemotionRules:
    """Test demotion criteria"""
    
    def test_should_demote_drawdown_breach(self):
        """Test demotion on drawdown breach"""
        live_metrics = {
            'max_drawdown': 0.15,  # Over limit
            'sharpe': 1.0,
            'position_drift_pct': 0.02
        }
        
        health_status = {'status': 'OK'}
        cfg = MeridianConfig()
        
        should_demote, reason = should_demote_to_disabled(
            live_metrics,
            health_status,
            cfg
        )
        
        assert should_demote is True
        assert "drawdown" in reason.lower()
    
    def test_should_demote_sharpe_degradation(self):
        """Test demotion on Sharpe degradation"""
        live_metrics = {
            'max_drawdown': 0.08,
            'sharpe': 0.3,  # Too low
            'position_drift_pct': 0.02
        }
        
        health_status = {'status': 'OK'}
        cfg = MeridianConfig()
        
        should_demote, reason = should_demote_to_disabled(
            live_metrics,
            health_status,
            cfg
        )
        
        assert should_demote is True
        assert "sharpe" in reason.lower()
    
    def test_should_demote_health_failures(self):
        """Test demotion on health failures"""
        live_metrics = {
            'max_drawdown': 0.08,
            'sharpe': 1.0,
            'position_drift_pct': 0.02
        }
        
        health_status = {
            'status': 'FAIL',
            'consecutive_failures': 5
        }
        
        cfg = MeridianConfig()
        
        should_demote, reason = should_demote_to_disabled(
            live_metrics,
            health_status,
            cfg
        )
        
        assert should_demote is True
        assert "health" in reason.lower() or "failure" in reason.lower()
    
    def test_should_not_demote_healthy(self):
        """Test no demotion for healthy strategy"""
        live_metrics = {
            'max_drawdown': 0.05,
            'sharpe': 1.2,
            'position_drift_pct': 0.01
        }
        
        health_status = {'status': 'OK'}
        cfg = MeridianConfig()
        
        should_demote, reason = should_demote_to_disabled(
            live_metrics,
            health_status,
            cfg
        )
        
        assert should_demote is False


class TestIncubationRunner:
    """Test incubation runner"""
    
    def test_update_strategy_state(self, tmp_path):
        """Test updating strategy state"""
        state_file = tmp_path / "runner_state.json"
        
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        status = update_strategy_state(
            "test_strategy",
            wfa_metrics,
            {},
            {},
            {'status': 'OK'},
            cfg,
            str(state_file)
        )
        
        assert status.strategy_name == "test_strategy"
        assert status.days_in_state >= 0
    
    def test_run_incubation_cycle(self):
        """Test running full incubation cycle"""
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        result = run_incubation_cycle(
            "test_strategy",
            wfa_metrics,
            {},
            {},
            {'status': 'OK'},
            cfg
        )
        
        assert 'strategy_name' in result
        assert 'current_state' in result
        assert 'days_in_state' in result


class TestIncubationReporter:
    """Test incubation reporting"""
    
    def test_generate_report(self, tmp_path):
        """Test report generation"""
        status = StrategyStatus(
            strategy_name="test_strategy",
            state=StrategyState.PAPER_TRADING,
            days_in_state=30
        )
        
        status.metadata = {
            'wfa_metrics': {'mean_oos_sharpe': 1.2},
            'health_status': {'status': 'OK'}
        }
        
        cycle_result = {
            'strategy_name': 'test_strategy',
            'current_state': 'paper_trading'
        }
        
        report_path = generate_incubation_report(
            status,
            cycle_result,
            str(tmp_path)
        )
        
        assert report_path.endswith('.md')
        assert Path(report_path).exists()


class TestFullLifecycle:
    """Test complete strategy lifecycle"""
    
    def test_research_to_paper_lifecycle(self, tmp_path):
        """Test promotion from Research through Paper"""
        state_file = tmp_path / "lifecycle_state.json"
        cfg = MeridianConfig()
        
        # Start in research
        status = StrategyStatus("lifecycle_test", StrategyState.RESEARCH)
        save_strategy_state(status, str(state_file))
        
        # Move to WFA_PASSED (manual)
        status.state = StrategyState.WFA_PASSED
        save_strategy_state(status, str(state_file))
        
        # Good WFA metrics should promote to paper
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        status = update_strategy_state(
            "lifecycle_test",
            wfa_metrics,
            {},
            {},
            {'status': 'OK'},
            cfg,
            str(state_file)
        )
        
        assert status.state == StrategyState.PAPER_TRADING
    
    def test_live_to_disabled_demotion(self, tmp_path):
        """Test demotion from Live to Disabled"""
        state_file = tmp_path / "demotion_state.json"
        cfg = MeridianConfig()
        
        # Start in live
        status = StrategyStatus("demotion_test", StrategyState.LIVE_TRADING)
        save_strategy_state(status, str(state_file))
        
        # Bad drawdown should disable
        live_metrics = {
            'max_drawdown': 0.20,  # Way over limit
            'sharpe': 0.5,
            'position_drift_pct': 0.02
        }
        
        status = update_strategy_state(
            "demotion_test",
            {},
            {},
            live_metrics,
            {'status': 'OK'},
            cfg,
            str(state_file)
        )
        
        assert status.state == StrategyState.DISABLED


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_promotion_deterministic(self):
        """Test that promotion rules are deterministic"""
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        cfg = MeridianConfig()
        
        result1 = can_promote_to_paper(wfa_metrics, cfg)
        result2 = can_promote_to_paper(wfa_metrics, cfg)
        
        assert result1 == result2


