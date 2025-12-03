"""
End-to-End Pipeline Integration Test

The MOST IMPORTANT test - validates entire Meridian system together.

Flow: Synthetic Data → Loaders → Strategy → Execution → PnL → Attribution → Incubation
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.synthetic import SyntheticDataset
from meridian_v2_1_2.execution.paper_sim import SimulatedBroker, SimulatedPerformance
from meridian_v2_1_2.performance import (
    compute_daily_pnl,
    attribute_to_assets,
    attribute_to_strategies
)
from meridian_v2_1_2.incubation import (
    run_incubation_cycle,
    load_strategy_state
)


class TestEndToEndPipeline:
    """
    The Grand Integration Test.
    
    Validates the ENTIRE Meridian system working together.
    """
    
    def test_complete_pipeline_30_days(self, tmp_path):
        """
        Test complete 30-day simulation pipeline.
        
        This is the most comprehensive test in Meridian.
        """
        # Configure system
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 30
        cfg.synthetic.seed = 42
        cfg.paper_sim.starting_capital = 100000.0
        cfg.incubation.state_path = str(tmp_path / "strategy_status.json")
        
        # Generate synthetic market
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD', 'LTPZ'])
        
        # Validate data generation
        assert 'prices' in data
        assert 'GLD' in data['prices']
        assert 'LTPZ' in data['prices']
        assert len(data['prices']['GLD']) == 30
        
        # Initialize paper broker
        broker = SimulatedBroker(
            starting_capital=cfg.paper_sim.starting_capital,
            config=cfg
        )
        
        # Initialize performance tracker
        perf = SimulatedPerformance()
        
        # Simulate 30 days of trading
        for day in range(30):
            # Get current prices
            current_prices = {
                'GLD': data['prices']['GLD']['close'].iloc[day],
                'LTPZ': data['prices']['LTPZ']['close'].iloc[day]
            }
            
            # Simple strategy: buy GLD on even days, buy LTPZ on odd days
            if day % 2 == 0 and day < 28:
                broker.submit_order('GLD', 10.0, 'buy')
            elif day % 2 == 1 and day < 28:
                broker.submit_order('LTPZ', 5.0, 'buy')
            
            # Generate fills (if there are pending orders)
            if day > 0:
                next_opens = {
                    'GLD': data['prices']['GLD']['open'].iloc[day],
                    'LTPZ': data['prices']['LTPZ']['open'].iloc[day]
                }
                broker.generate_fills(current_prices, next_opens)
            
            # Update market values
            broker.update_market_values(current_prices)
            
            # Track performance
            portfolio = broker.get_positions()
            perf.update(f"day_{day}", portfolio['equity'])
        
        # ASSERTIONS: Validate entire pipeline worked
        
        # 1. NO NaNs anywhere
        assert not data['prices']['GLD'].isna().any().any()
        assert not data['prices']['LTPZ'].isna().any().any()
        
        # 2. Orders were created and filled
        filled_orders = broker.get_filled_orders()
        assert len(filled_orders) > 0, "No orders were filled"
        
        # 3. Portfolio has positions
        final_portfolio = broker.get_positions()
        assert len(final_portfolio['positions']) > 0, "No positions held"
        
        # 4. PnL series exists
        assert len(perf.equity_history) == 30
        # PnL may be flat if no fills occurred, which is acceptable
        assert isinstance(perf.equity_history[0], (int, float))
        
        # 5. Performance metrics are valid
        metrics = perf.get_metrics()
        assert 'sharpe' in metrics
        assert 'max_drawdown' in metrics
        assert isinstance(metrics['sharpe'], float)
        
        # 6. Final equity is reasonable
        assert final_portfolio['equity'] > 0
        assert final_portfolio['equity'] < 200000  # Within 2x starting capital
        
        # 7. Attribution can be computed
        import pandas as pd
        
        # Create position series (constant positions over time for simplicity)
        position_series = {}
        for symbol, pos in final_portfolio['positions'].items():
            position_series[symbol] = pd.Series(
                pos['qty'],
                index=data['prices'][symbol]['close'].index
            )
        
        prices_dict = {
            'GLD': data['prices']['GLD']['close'],
            'LTPZ': data['prices']['LTPZ']['close']
        }
        
        asset_attribution = attribute_to_assets(position_series, prices_dict)
        assert isinstance(asset_attribution, dict)
        
        # 8. Incubation cycle can run
        incubation_result = run_incubation_cycle(
            "test_strategy",
            wfa_metrics={'mean_oos_sharpe': 0.5},
            paper_metrics={'sharpe': 0.6, 'max_drawdown': 0.05},
            live_metrics={},
            health_status={'status': 'OK'},
            cfg=cfg
        )
        
        assert 'strategy_name' in incubation_result
        assert 'current_state' in incubation_result
        
        print(f"\n✅ COMPLETE E2E PIPELINE TEST PASSED!")
        print(f"   Orders Filled: {len(filled_orders)}")
        print(f"   Final Equity: ${final_portfolio['equity']:,.2f}")
        print(f"   Sharpe: {metrics['sharpe']:.2f}")
        print(f"   Max DD: {metrics['max_drawdown']:.2%}")
    
    def test_pipeline_handles_no_trades(self):
        """Test pipeline gracefully handles no trading activity"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 50  # Enough for monthly data
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD'])
        
        broker = SimulatedBroker(config=cfg)
        perf = SimulatedPerformance()
        
        # Run 10 days with NO orders
        for day in range(10):
            current_prices = {'GLD': data['prices']['GLD']['close'].iloc[day]}
            broker.update_market_values(current_prices)
            portfolio = broker.get_positions()
            perf.update(f"day_{day}", portfolio['equity'])
        
        # Should still work, just no activity
        assert len(perf.equity_history) == 10
        assert all(eq == cfg.paper_sim.starting_capital for eq in perf.equity_history)
    
    def test_pipeline_deterministic(self, tmp_path):
        """Test pipeline produces deterministic results"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 100  # Need at least ~21 days for monthly macro data
        cfg.synthetic.seed = 99
        cfg.incubation.state_path = str(tmp_path / "det_test.json")
        
        # Run 1
        dataset1 = SyntheticDataset(cfg)
        data1 = dataset1.generate(symbols=['GLD'])
        
        # Run 2
        dataset2 = SyntheticDataset(cfg)
        data2 = dataset2.generate(symbols=['GLD'])
        
        # Should be identical
        assert data1['prices']['GLD']['close'].equals(data2['prices']['GLD']['close'])
    
    def test_pipeline_stress_high_volatility(self):
        """Test pipeline under high volatility conditions"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 50
        cfg.synthetic.vol_high = 0.05  # 5% daily vol (extreme)
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate_stress_scenario('crash')
        
        broker = SimulatedBroker(config=cfg)
        
        # Trade through crash
        for day in range(min(50, len(data['prices']['GLD']))):
            if day % 5 == 0 and day < 45:
                broker.submit_order('GLD', 5.0, 'buy')
            
            current_prices = {'GLD': data['prices']['GLD']['close'].iloc[day]}
            
            if day > 0:
                next_opens = {'GLD': data['prices']['GLD']['open'].iloc[day]}
                broker.generate_fills(current_prices, next_opens)
            
            broker.update_market_values(current_prices)
        
        # System should survive (no crashes)
        portfolio = broker.get_positions()
        assert portfolio['equity'] > 0  # Still solvent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

