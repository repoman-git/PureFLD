"""
Incubation State Flow Integration Test

Tests strategy promotion/demotion through lifecycle.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.incubation import (
    StrategyState,
    update_strategy_state,
    load_strategy_state
)


class TestIncubationStateFlow:
    """Test complete incubation lifecycle"""
    
    def test_promotion_flow_wfa_to_live(self, tmp_path):
        """Test promotion from WFA through to Live"""
        cfg = MeridianConfig()
        cfg.incubation.state_path = str(tmp_path / "incub_state.json")
        cfg.incubation.allow_auto_promotion = True
        cfg.incubation.require_manual_live_approval = False
        
        # Start at WFA_PASSED
        status = load_strategy_state("test_strategy", cfg.incubation.state_path)
        status.state = StrategyState.WFA_PASSED
        
        from meridian_v2_1_2.incubation import save_strategy_state
        save_strategy_state(status, cfg.incubation.state_path)
        
        # Good WFA metrics should promote to paper
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'overfit_index': 1.3,
            'win_rate': 0.6,
            'stability_score': 2.0
        }
        
        status = update_strategy_state(
            "test_strategy",
            wfa_metrics=wfa_metrics,
            paper_metrics={},
            live_metrics={},
            health_status={'status': 'OK'},
            cfg=cfg,
            state_path=cfg.incubation.state_path
        )
        
        # Should be promoted to paper
        assert status.state == StrategyState.PAPER_TRADING
        
        # Simulate paper trading for 50 days
        for day in range(50):
            status.days_in_state += 1
            save_strategy_state(status, cfg.incubation.state_path)
        
        # Good paper metrics should promote to live
        paper_metrics = {
            'sharpe': 1.0,
            'max_drawdown': 0.08
        }
        
        status = update_strategy_state(
            "test_strategy",
            wfa_metrics=wfa_metrics,
            paper_metrics=paper_metrics,
            live_metrics={},
            health_status={'status': 'OK'},
            cfg=cfg,
            state_path=cfg.incubation.state_path
        )
        
        # Should be promoted to live
        assert status.state == StrategyState.LIVE_TRADING
    
    def test_demotion_flow_live_to_disabled(self, tmp_path):
        """Test demotion from Live to Disabled"""
        cfg = MeridianConfig()
        cfg.incubation.state_path = str(tmp_path / "demotion_state.json")
        cfg.incubation.allow_auto_demotion = True
        
        # Start at LIVE
        status = load_strategy_state("failing_strategy", cfg.incubation.state_path)
        status.state = StrategyState.LIVE_TRADING
        
        from meridian_v2_1_2.incubation import save_strategy_state
        save_strategy_state(status, cfg.incubation.state_path)
        
        # Bad drawdown should demote
        live_metrics = {
            'max_drawdown': 0.15,  # Over 12% limit
            'sharpe': 0.3,
            'position_drift_pct': 0.02
        }
        
        status = update_strategy_state(
            "failing_strategy",
            wfa_metrics={},
            paper_metrics={},
            live_metrics=live_metrics,
            health_status={'status': 'OK'},
            cfg=cfg,
            state_path=cfg.incubation.state_path
        )
        
        # Should be disabled
        assert status.state == StrategyState.DISABLED


