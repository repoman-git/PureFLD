"""
Comprehensive test suite for EOD Engine in Meridian v2.1.2.

Tests verify end-of-day workflow, data fetching, signal generation, and order building.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
from datetime import datetime, time

from meridian_v2_1_2 import MeridianConfig
from meridian_v2_1_2.eod_engine import (
    EODScheduler,
    should_run_today,
    fetch_eod_data,
    run_eod_signals,
    get_latest_signals,
    build_eod_orders,
    validate_orders,
    execute_eod_cycle,
    EODOrder,
    EODLogger,
    log_eod_results
)


class TestEODScheduler:
    """Test EOD scheduling logic"""
    
    def test_should_run_on_weekdays(self):
        """
        TEST 1: EOD should run on weekdays
        """
        # Monday
        monday = datetime(2024, 1, 1)  # Jan 1, 2024 is Monday
        assert should_run_today(monday, skip_weekends=True)
        
        # Saturday
        saturday = datetime(2024, 1, 6)  # Jan 6, 2024 is Saturday
        assert not should_run_today(saturday, skip_weekends=True)
    
    def test_scheduler_time_check(self):
        """
        TEST: Scheduler checks time correctly
        """
        scheduler = EODScheduler(run_time=time(16, 30))
        
        # Before run time
        before = datetime(2024, 1, 1, 16, 0)  # 4:00 PM
        assert not scheduler.should_run_now(before)
        
        # After run time
        after = datetime(2024, 1, 1, 17, 0)  # 5:00 PM
        assert scheduler.should_run_now(after)


class TestEODDataFetcher:
    """Test EOD data fetching"""
    
    def test_fetches_daily_bars(self):
        """
        TEST 2: Data fetcher returns daily bars
        """
        symbols = ['GLD', 'LTPZ']
        
        eod_data = fetch_eod_data(symbols, lookback_days=100, source="local")
        
        # Should have data for both symbols
        assert 'GLD' in eod_data
        assert 'LTPZ' in eod_data
        
        # Should have OHLCV columns
        assert 'close' in eod_data['GLD'].columns
        assert 'open' in eod_data['GLD'].columns
    
    def test_data_is_daily_frequency(self):
        """
        TEST: Data is daily frequency (not intraday)
        """
        symbols = ['GLD']
        
        eod_data = fetch_eod_data(symbols, lookback_days=50, source="local")
        
        df = eod_data['GLD']
        
        # Check frequency is daily
        assert len(df) > 0
        # Daily data should have reasonable length
        assert 10 < len(df) < 100


class TestEODOrderBuilder:
    """Test EOD order building"""
    
    def test_builds_orders_for_position_delta(self):
        """
        TEST 3: Order builder creates orders for position deltas
        """
        target_positions = {'GLD': 10.0, 'LTPZ': -5.0}
        current_positions = {'GLD': 5.0, 'LTPZ': 0.0}
        latest_prices = {'GLD': 180.0, 'LTPZ': 50.0}
        
        orders = build_eod_orders(target_positions, current_positions, latest_prices)
        
        # Should have 2 orders
        assert len(orders) == 2
        
        # GLD: need to buy 5 more (10 - 5)
        gld_order = [o for o in orders if o.symbol == 'GLD'][0]
        assert gld_order.side == 'buy'
        assert abs(gld_order.quantity - 5.0) < 0.01
        
        # LTPZ: need to sell 5 (-5 - 0)
        ltpz_order = [o for o in orders if o.symbol == 'LTPZ'][0]
        assert ltpz_order.side == 'sell'
        assert abs(ltpz_order.quantity - 5.0) < 0.01
    
    def test_validates_orders(self):
        """
        TEST: Order validation catches invalid orders
        """
        # Valid orders
        valid_orders = [
            EODOrder(symbol='GLD', side='buy', quantity=10, order_type='moo'),
            EODOrder(symbol='LTPZ', side='sell', quantity=5, order_type='moo')
        ]
        
        assert validate_orders(valid_orders, max_orders_per_day=100)
        
        # Too many orders
        many_orders = [EODOrder(symbol=f'SYM{i}', side='buy', quantity=1, order_type='moo') for i in range(150)]
        
        with pytest.raises(ValueError, match="Too many orders"):
            validate_orders(many_orders, max_orders_per_day=100)


class TestEODExecutionCycle:
    """Test complete EOD execution cycle"""
    
    def test_eod_cycle_executes(self):
        """
        TEST 4: Complete EOD cycle executes successfully
        """
        config = MeridianConfig(mode="research")
        symbols = ['GLD', 'LTPZ']
        
        results = execute_eod_cycle(config, symbols)
        
        # Should have all expected keys
        assert 'signals' in results
        assert 'orders' in results
        assert 'target_positions' in results
        assert 'timestamp' in results
    
    def test_eod_cycle_deterministic(self):
        """
        TEST: EOD cycle is deterministic
        """
        config = MeridianConfig(mode="research")
        symbols = ['GLD']
        current_positions = {'GLD': 0.0}
        
        results1 = execute_eod_cycle(config, symbols, current_positions)
        results2 = execute_eod_cycle(config, symbols, current_positions)
        
        # Signals should be identical
        assert results1['signals'] == results2['signals']


class TestEODLogging:
    """Test EOD logging system"""
    
    def test_logger_creates_files(self):
        """
        TEST 5: EOD logger writes log files
        """
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            results = {
                'timestamp': datetime.now(),
                'symbols': ['GLD', 'LTPZ'],
                'signals': {'GLD': 1, 'LTPZ': -1},
                'num_orders': 2
            }
            
            logger = EODLogger(log_dir=temp_dir)
            logger.log_cycle(results)
            
            # Check that log file was created
            log_files = list(Path(temp_dir).glob('*.json'))
            assert len(log_files) > 0
            
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


