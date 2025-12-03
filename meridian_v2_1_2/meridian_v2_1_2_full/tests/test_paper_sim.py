"""
Test suite for Paper Trading Simulation

Tests complete offline execution simulator.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.execution.paper_sim import (
    SimulatedOrder,
    OrderStatus,
    OrderSide,
    SimulatedPortfolio,
    SimulatedBroker,
    generate_fill,
    apply_slippage,
    simple_bps_slippage,
    SimulatedOMS,
    write_oms_logs,
    SimulatedPerformance,
    reconcile_positions,
    check_position_drift
)
from meridian_v2_1_2.config import MeridianConfig


class TestSimulatedOrder:
    """Test simulated order object"""
    
    def test_order_creation(self):
        """Test creating an order"""
        order = SimulatedOrder(
            order_id="test_123",
            symbol="GLD",
            qty=10.0,
            side=OrderSide.BUY
        )
        
        assert order.order_id == "test_123"
        assert order.symbol == "GLD"
        assert order.qty == 10.0
        assert order.side == OrderSide.BUY
    
    def test_order_to_dict(self):
        """Test order serialization"""
        order = SimulatedOrder(
            order_id="test_123",
            symbol="GLD",
            qty=10.0,
            side=OrderSide.BUY,
            status=OrderStatus.FILLED
        )
        
        order_dict = order.to_dict()
        
        assert order_dict['order_id'] == "test_123"
        assert order_dict['symbol'] == "GLD"
        assert order_dict['qty'] == 10.0
        assert order_dict['side'] == "buy"
        assert order_dict['status'] == "filled"


class TestSimulatedPortfolio:
    """Test simulated portfolio"""
    
    def test_portfolio_initialization(self):
        """Test portfolio starts with cash"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        
        assert portfolio.cash == 100000.0
        assert portfolio.starting_capital == 100000.0
        assert len(portfolio.positions) == 0
    
    def test_buy_position(self):
        """Test buying a position"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        
        # Buy 10 shares at $100
        portfolio.update_position("GLD", 10.0, 100.0)
        
        pos = portfolio.get_position("GLD")
        assert pos.qty == 10.0
        assert pos.avg_cost == 100.0
        assert portfolio.cash == 99000.0  # 100000 - 1000
    
    def test_sell_position(self):
        """Test selling a position"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        
        # Buy then sell
        portfolio.update_position("GLD", 10.0, 100.0)
        portfolio.update_position("GLD", -5.0, 110.0)
        
        pos = portfolio.get_position("GLD")
        assert pos.qty == 5.0
        assert portfolio.realized_pl == 50.0  # 5 shares * $10 profit
    
    def test_short_position(self):
        """Test shorting"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        
        # Short 10 shares at $100
        portfolio.update_position("LTPZ", -10.0, 100.0)
        
        pos = portfolio.get_position("LTPZ")
        assert pos.qty == -10.0
        assert pos.avg_cost == 100.0
    
    def test_market_value_update(self):
        """Test updating market values"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        portfolio.update_position("GLD", 10.0, 100.0)
        
        # Update to $110
        portfolio.update_market_values({"GLD": 110.0})
        
        pos = portfolio.get_position("GLD")
        assert pos.market_value == 1100.0
        assert pos.unrealized_pl == 100.0
    
    def test_total_equity(self):
        """Test total equity calculation"""
        portfolio = SimulatedPortfolio(starting_capital=100000.0)
        portfolio.update_position("GLD", 10.0, 100.0)
        portfolio.update_market_values({"GLD": 110.0})
        
        equity = portfolio.get_total_equity()
        assert equity == 100100.0  # 99000 cash + 1100 position


class TestSlippageModel:
    """Test slippage calculations"""
    
    def test_buy_slippage(self):
        """Test buy slippage increases price"""
        price = 100.0
        slipped = simple_bps_slippage(price, 5.0, "buy")
        
        # 5 bps = 0.05%
        expected = 100.0 * (1 + 0.0005)
        assert slipped == pytest.approx(expected, rel=0.001)
    
    def test_sell_slippage(self):
        """Test sell slippage decreases price"""
        price = 100.0
        slipped = simple_bps_slippage(price, 5.0, "sell")
        
        # 5 bps = 0.05%
        expected = 100.0 * (1 - 0.0005)
        assert slipped == pytest.approx(expected, rel=0.001)


class TestFillSimulation:
    """Test fill generation"""
    
    def test_generate_fill_eod(self):
        """Test EOD fill generation"""
        order = SimulatedOrder(
            order_id="test",
            symbol="GLD",
            qty=10.0,
            side=OrderSide.BUY
        )
        
        fill_price = generate_fill(order, 100.0, 101.0, slippage_bps=5.0)
        
        # Should be next_open (101) + slippage
        assert fill_price > 101.0
        assert fill_price < 102.0
    
    def test_generate_fill_without_gap(self):
        """Test fill without gap model"""
        order = SimulatedOrder(
            order_id="test",
            symbol="GLD",
            qty=10.0,
            side=OrderSide.BUY
        )
        
        fill_price = generate_fill(
            order, 100.0, None, 
            slippage_bps=5.0, 
            use_gap_model=False
        )
        
        # Should be current price + slippage
        assert fill_price > 100.0
        assert fill_price < 101.0


class TestSimulatedBroker:
    """Test simulated broker"""
    
    def test_broker_initialization(self):
        """Test broker starts correctly"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(starting_capital=100000.0, config=cfg)
        
        assert broker.portfolio.cash == 100000.0
        assert len(broker.orders) == 0
    
    def test_submit_order(self):
        """Test order submission"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(config=cfg)
        
        order = broker.submit_order("GLD", 10.0, "buy")
        
        assert order.symbol == "GLD"
        assert order.qty == 10.0
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.SUBMITTED
    
    def test_cancel_order(self):
        """Test order cancellation"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(config=cfg)
        
        order = broker.submit_order("GLD", 10.0, "buy")
        result = broker.cancel_order(order.order_id)
        
        assert result is True
        assert order.status == OrderStatus.CANCELLED
    
    def test_generate_fills(self):
        """Test fill generation"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(starting_capital=100000.0, config=cfg)
        
        # Submit order
        order = broker.submit_order("GLD", 10.0, "buy")
        
        # Generate fills
        fills = broker.generate_fills(
            current_prices={"GLD": 100.0},
            next_opens={"GLD": 101.0}
        )
        
        assert len(fills) == 1
        assert fills[0]['symbol'] == "GLD"
        assert order.status == OrderStatus.FILLED
    
    def test_portfolio_update_after_fill(self):
        """Test portfolio updates after fill"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(starting_capital=100000.0, config=cfg)
        
        broker.submit_order("GLD", 10.0, "buy")
        broker.generate_fills(
            current_prices={"GLD": 100.0},
            next_opens={"GLD": 101.0}
        )
        
        portfolio = broker.get_positions()
        assert "GLD" in portfolio['positions']
        assert portfolio['positions']['GLD']['qty'] == 10.0


class TestSimulatedOMS:
    """Test OMS logging"""
    
    def test_oms_initialization(self, tmp_path):
        """Test OMS creates log directory"""
        oms = SimulatedOMS(str(tmp_path / "oms_logs"))
        
        assert oms.log_path.exists()
    
    def test_write_orders(self, tmp_path):
        """Test writing orders log"""
        oms = SimulatedOMS(str(tmp_path / "oms_logs"))
        
        order = SimulatedOrder(
            order_id="test_123",
            symbol="GLD",
            qty=10.0,
            side=OrderSide.BUY
        )
        
        log_file = oms.write_orders([order], "20240101")
        
        assert Path(log_file).exists()
    
    def test_write_fills(self, tmp_path):
        """Test writing fills log"""
        oms = SimulatedOMS(str(tmp_path / "oms_logs"))
        
        fills = [
            {'order_id': 'test_123', 'symbol': 'GLD', 'qty': 10.0, 'price': 100.5}
        ]
        
        log_file = oms.write_fills(fills, "20240101")
        
        assert Path(log_file).exists()


class TestSimulatedPerformance:
    """Test performance tracking"""
    
    def test_performance_initialization(self):
        """Test performance tracker starts empty"""
        perf = SimulatedPerformance()
        
        assert len(perf.equity_history) == 0
        assert len(perf.dates) == 0
    
    def test_update_equity(self):
        """Test updating equity"""
        perf = SimulatedPerformance()
        
        perf.update("2024-01-01", 100000.0)
        perf.update("2024-01-02", 101000.0)
        
        assert len(perf.equity_history) == 2
        assert perf.equity_history[-1] == 101000.0
    
    def test_total_return(self):
        """Test total return calculation"""
        perf = SimulatedPerformance()
        
        perf.update("2024-01-01", 100000.0)
        perf.update("2024-01-02", 110000.0)
        
        total_return = perf.get_total_return()
        assert total_return == pytest.approx(0.10, rel=0.01)
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        perf = SimulatedPerformance()
        
        # Add some returns
        for i in range(252):
            equity = 100000 * (1.0 + 0.001 * i)
            perf.update(f"2024-{i:03d}", equity)
        
        sharpe = perf.get_sharpe_ratio()
        assert isinstance(sharpe, float)
    
    def test_max_drawdown(self):
        """Test max drawdown calculation"""
        perf = SimulatedPerformance()
        
        perf.update("2024-01-01", 100000.0)
        perf.update("2024-01-02", 110000.0)
        perf.update("2024-01-03", 90000.0)  # Drawdown from peak
        
        max_dd = perf.get_max_drawdown()
        expected_dd = (90000 - 110000) / 110000
        
        assert max_dd == pytest.approx(expected_dd, rel=0.01)


class TestReconciliation:
    """Test reconciliation"""
    
    def test_reconcile_matching_positions(self):
        """Test reconciliation with matching positions"""
        broker_positions = {
            'positions': {
                'GLD': {'qty': 10.0, 'avg_cost': 100.0}
            }
        }
        
        expected_positions = {'GLD': 10.0}
        
        is_reconciled, issues = reconcile_positions(
            broker_positions,
            expected_positions
        )
        
        assert is_reconciled is True
        assert len(issues) == 0
    
    def test_reconcile_drift(self):
        """Test reconciliation detects drift"""
        broker_positions = {
            'positions': {
                'GLD': {'qty': 10.0, 'avg_cost': 100.0}
            }
        }
        
        expected_positions = {'GLD': 15.0}
        
        is_reconciled, issues = reconcile_positions(
            broker_positions,
            expected_positions,
            tolerance=0.01
        )
        
        assert is_reconciled is False
        assert len(issues) > 0
    
    def test_check_position_drift(self):
        """Test position drift checking"""
        current = {'GLD': 10.0}
        target = {'GLD': 10.5}
        
        has_drift, drift_by_symbol = check_position_drift(
            current,
            target,
            max_drift_pct=0.10
        )
        
        assert has_drift is False  # 5% drift is < 10% tolerance
        assert 'GLD' in drift_by_symbol


class TestEndToEnd:
    """End-to-end paper trading tests"""
    
    def test_full_trading_cycle(self):
        """Test complete trading cycle"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(starting_capital=100000.0, config=cfg)
        
        # Day 1: Submit order
        order = broker.submit_order("GLD", 10.0, "buy")
        
        # Day 2: Fill order
        fills = broker.generate_fills(
            current_prices={"GLD": 100.0},
            next_opens={"GLD": 101.0}
        )
        
        assert len(fills) == 1
        assert order.status == OrderStatus.FILLED
        
        # Check portfolio
        portfolio = broker.get_positions()
        assert "GLD" in portfolio['positions']
        assert portfolio['positions']['GLD']['qty'] == 10.0
    
    def test_multi_day_simulation(self):
        """Test multi-day simulation"""
        cfg = MeridianConfig()
        broker = SimulatedBroker(starting_capital=100000.0, config=cfg)
        perf = SimulatedPerformance()
        
        # Day 1
        broker.submit_order("GLD", 10.0, "buy")
        broker.generate_fills({"GLD": 100.0}, {"GLD": 101.0})
        broker.update_market_values({"GLD": 101.0})
        
        portfolio = broker.get_positions()
        perf.update("2024-01-01", portfolio['equity'])
        
        # Day 2
        broker.update_market_values({"GLD": 105.0})
        portfolio = broker.get_positions()
        perf.update("2024-01-02", portfolio['equity'])
        
        # Check performance
        metrics = perf.get_metrics()
        assert metrics['total_return'] > 0


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_fill_generation_deterministic(self):
        """Test fills are deterministic"""
        order1 = SimulatedOrder("test", "GLD", 10.0, OrderSide.BUY)
        order2 = SimulatedOrder("test", "GLD", 10.0, OrderSide.BUY)
        
        fill1 = generate_fill(order1, 100.0, 101.0, slippage_bps=5.0)
        fill2 = generate_fill(order2, 100.0, 101.0, slippage_bps=5.0)
        
        assert fill1 == fill2

