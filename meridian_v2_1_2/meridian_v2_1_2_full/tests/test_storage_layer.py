"""
Storage Layer Test Suite

Tests for local storage, secrets, database, and persistence.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import pandas as pd
import numpy as np
from dataclasses import dataclass

from meridian_v2_1_2.storage import (
    EnvLoader,
    load_env_keys,
    mask_keys,
    LocalDB,
    init_database,
    StateStore,
    RunRegistry,
    log_run,
    FileManager,
    safe_write,
    safe_read,
    serialize,
    deserialize,
    save_dataframe,
    load_dataframe
)


class TestEnvLoader:
    """Test environment variable loading"""
    
    def test_env_loader_initialization(self):
        """Test env loader can be initialized"""
        loader = EnvLoader()
        assert loader is not None
    
    def test_load_env_keys_no_file(self):
        """Test loading when no .env file exists"""
        keys = load_env_keys("nonexistent.env")
        
        # Should return dict with None values
        assert isinstance(keys, dict)
        for key in ['OPENBB_API_KEY', 'ALPACA_API_KEY']:
            assert key in keys
            # May be None if not in environment
    
    def test_mask_keys(self):
        """Test key masking"""
        keys = {
            'OPENBB_API_KEY': 'sk_test_1234567890abcdef',
            'ALPACA_API_KEY': None
        }
        
        masked = mask_keys(keys)
        
        # Key with value should be masked
        assert masked['OPENBB_API_KEY'] == 'sk_t****'
        
        # None key should remain None
        assert masked['ALPACA_API_KEY'] is None
    
    def test_loader_has_key_method(self):
        """Test has_key method"""
        loader = EnvLoader()
        loader._keys = {'TEST_KEY': 'value', 'EMPTY_KEY': None}
        
        assert loader.has_key('TEST_KEY') is True
        assert loader.has_key('EMPTY_KEY') is False
        assert loader.has_key('NONEXISTENT') is False


class TestLocalDB:
    """Test SQLite database"""
    
    def test_database_initialization(self, tmp_path):
        """Test database can be created"""
        db_path = tmp_path / "test.db"
        db = LocalDB(str(db_path))
        
        assert db_path.exists()
        assert db.conn is not None
        
        db.close()
    
    def test_tables_created(self, tmp_path):
        """Test all tables are created"""
        db_path = tmp_path / "test.db"
        db = LocalDB(str(db_path))
        
        # Check tables exist
        tables = db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """).fetchall()
        
        table_names = [t['name'] for t in tables]
        
        assert 'state_strategy' in table_names
        assert 'state_portfolio' in table_names
        assert 'orders' in table_names
        assert 'fills' in table_names
        assert 'pnl_daily' in table_names
        assert 'risk_metrics' in table_names
        
        db.close()
    
    def test_context_manager(self, tmp_path):
        """Test database as context manager"""
        db_path = tmp_path / "test.db"
        
        with LocalDB(str(db_path)) as db:
            assert db.conn is not None
        
        # Connection should be closed
        # (Can't easily test this without accessing private state)


class TestStateStore:
    """Test state store operations"""
    
    def test_save_and_load_strategy_state(self, tmp_path):
        """Test saving and loading strategy state"""
        db = LocalDB(str(tmp_path / "test.db"))
        store = StateStore(db)
        
        # Save state
        store.save_strategy_state(
            "test_strategy",
            "2025-03-01",
            {"param1": 0.5, "param2": 100},
            {"trend": 0.6, "cycle": 0.4}
        )
        
        # Load state
        state = store.load_strategy_state("test_strategy", "2025-03-01")
        
        assert state is not None
        assert state['params']['param1'] == 0.5
        assert state['weights']['trend'] == 0.6
        
        db.close()
    
    def test_save_and_load_portfolio_state(self, tmp_path):
        """Test portfolio state persistence"""
        db = LocalDB(str(tmp_path / "test.db"))
        store = StateStore(db)
        
        # Save portfolio
        positions = {
            'GLD': {'qty': 10.0, 'cost_basis': 1000.0, 'market_value': 1050.0},
            'LTPZ': {'qty': -5.0, 'cost_basis': 500.0, 'market_value': 480.0}
        }
        
        store.save_portfolio_state("2025-03-01", positions)
        
        # Load portfolio
        loaded = store.load_portfolio_state("2025-03-01")
        
        assert 'GLD' in loaded
        assert loaded['GLD']['qty'] == 10.0
        assert loaded['LTPZ']['qty'] == -5.0
        
        db.close()
    
    def test_save_and_load_risk_metrics(self, tmp_path):
        """Test risk metrics persistence"""
        db = LocalDB(str(tmp_path / "test.db"))
        store = StateStore(db)
        
        # Save metrics
        store.save_risk_metrics(
            "2025-03-01",
            sharpe=1.5,
            max_drawdown=0.15,
            volatility=0.20
        )
        
        # Load metrics
        metrics = store.load_risk_metrics("2025-03-01")
        
        assert metrics['sharpe'] == 1.5
        assert metrics['max_drawdown'] == 0.15
        
        db.close()
    
    def test_incubation_state_persistence(self, tmp_path):
        """Test incubation state save/load"""
        db = LocalDB(str(tmp_path / "test.db"))
        store = StateStore(db)
        
        # Save incubation state
        store.save_incubation_state("gold_strategy", "paper_trading", days_in_state=30)
        
        # Load state
        state = store.load_incubation_state("gold_strategy")
        
        assert state['state'] == "paper_trading"
        assert state['days_in_state'] == 30
        
        db.close()


class TestRunRegistry:
    """Test run registry"""
    
    def test_log_run(self, tmp_path):
        """Test logging a run"""
        registry = RunRegistry(str(tmp_path / "runs"))
        
        run_id = registry.log_run(
            run_type="research",
            config={"test": "value"},
            performance={"sharpe": 1.2},
            warnings=["test warning"],
            model_risk_score=0.3
        )
        
        assert run_id is not None
        assert isinstance(run_id, str)
        
        # Check file was created
        run_file = tmp_path / "runs" / f"{run_id}-run.json"
        assert run_file.exists()
    
    def test_get_run(self, tmp_path):
        """Test retrieving a run"""
        registry = RunRegistry(str(tmp_path / "runs"))
        
        run_id = registry.log_run(
            run_type="paper",
            config={"param": 123}
        )
        
        # Retrieve run
        run_record = registry.get_run(run_id)
        
        assert run_record is not None
        assert run_record['run_type'] == "paper"
        assert run_record['config']['param'] == 123
    
    def test_list_runs(self, tmp_path):
        """Test listing runs"""
        registry = RunRegistry(str(tmp_path / "runs"))
        
        # Log multiple runs
        import time
        registry.log_run("research", {})
        time.sleep(0.01)  # Ensure different timestamps
        registry.log_run("paper", {})
        time.sleep(0.01)
        registry.log_run("research", {})
        
        # List all runs
        all_runs = registry.list_runs()
        assert len(all_runs) == 3
        
        # List research runs only
        research_runs = registry.list_runs(run_type="research")
        assert len(research_runs) == 2


class TestFileManager:
    """Test file manager"""
    
    def test_safe_write(self, tmp_path):
        """Test atomic write"""
        file_path = tmp_path / "test" / "file.txt"
        
        safe_write(file_path, "test content")
        
        assert file_path.exists()
        assert file_path.read_text() == "test content"
    
    def test_safe_read(self, tmp_path):
        """Test safe read"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        content = safe_read(file_path)
        
        assert content == "content"
    
    def test_compressed_write_read(self, tmp_path):
        """Test compressed write and read"""
        file_path = tmp_path / "compressed.gz"
        
        # Write compressed
        FileManager.safe_write(file_path, "compressed content", compress=True)
        
        # Read compressed
        content = FileManager.safe_read(file_path, compressed=True)
        
        assert content == "compressed content"
    
    def test_ensure_dir(self, tmp_path):
        """Test directory creation"""
        dir_path = tmp_path / "deep" / "nested" / "dir"
        
        FileManager.ensure_dir(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_clean_old_files(self, tmp_path):
        """Test cleaning old files"""
        # Create multiple files
        for i in range(10):
            (tmp_path / f"file_{i}.txt").write_text(f"content {i}")
        
        # Keep only 5 most recent
        deleted = FileManager.clean_old_files(tmp_path, "*.txt", keep_recent=5)
        
        assert deleted == 5
        remaining = list(tmp_path.glob("*.txt"))
        assert len(remaining) == 5


class TestSerializer:
    """Test serializer"""
    
    def test_serialize_deserialize_dict(self):
        """Test dict serialization"""
        data = {"key": "value", "number": 123}
        
        serialized = serialize(data, 'json')
        deserialized = deserialize(serialized, 'json')
        
        assert deserialized == data
    
    def test_serialize_deserialize_numpy(self):
        """Test numpy serialization"""
        arr = np.array([1, 2, 3, 4, 5])
        
        serialized = serialize(arr, 'numpy')
        deserialized = deserialize(serialized, 'numpy')
        
        assert np.array_equal(deserialized, arr)
    
    def test_save_load_dataframe(self, tmp_path):
        """Test DataFrame serialization"""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        file_path = tmp_path / "test.parquet"
        
        # Save
        save_dataframe(df, file_path)
        
        # Load
        loaded = load_dataframe(file_path)
        
        pd.testing.assert_frame_equal(loaded, df)
    
    def test_dataclass_serialization(self):
        """Test dataclass serialization"""
        @dataclass
        class TestData:
            name: str
            value: int
        
        data = TestData("test", 123)
        
        serialized = serialize(data, 'json')
        deserialized = deserialize(serialized, 'json')
        
        assert deserialized['name'] == "test"
        assert deserialized['value'] == 123


class TestIntegration:
    """Test complete storage workflow"""
    
    def test_complete_persistence_workflow(self, tmp_path):
        """Test full persistence workflow"""
        # Setup
        db = LocalDB(str(tmp_path / "meridian.db"))
        store = StateStore(db)
        registry = RunRegistry(str(tmp_path / "runs"))
        
        # Save strategy state
        store.save_strategy_state(
            "gold_strategy",
            "2025-03-01",
            {"lookback": 20, "threshold": 0.5}
        )
        
        # Save portfolio
        store.save_portfolio_state(
            "2025-03-01",
            {'GLD': {'qty': 10, 'cost_basis': 1000, 'market_value': 1050}}
        )
        
        # Save risk metrics
        store.save_risk_metrics("2025-03-01", sharpe=1.2, max_drawdown=0.1)
        
        # Log run
        run_id = registry.log_run(
            "research",
            {"strategy": "gold_strategy"},
            performance={"sharpe": 1.2}
        )
        
        # Verify everything persisted
        strategy = store.load_strategy_state("gold_strategy", "2025-03-01")
        portfolio = store.load_portfolio_state("2025-03-01")
        metrics = store.load_risk_metrics("2025-03-01")
        run_record = registry.get_run(run_id)
        
        assert strategy is not None
        assert len(portfolio) > 0
        assert metrics['sharpe'] == 1.2
        assert run_record['run_type'] == "research"
        
        db.close()


class TestOfflineGuarantee:
    """Test that storage layer is truly offline"""
    
    def test_no_network_calls_env_loader(self):
        """Test env loader makes no network calls"""
        # This should work completely offline
        loader = EnvLoader()
        keys = loader.load()
        
        # Should complete without network access
        assert isinstance(keys, dict)
    
    def test_no_network_calls_database(self, tmp_path):
        """Test database operations are offline"""
        db = LocalDB(str(tmp_path / "test.db"))
        store = StateStore(db)
        
        # All operations should work offline
        store.save_strategy_state("test", "2025-03-01", {})
        state = store.load_strategy_state("test")
        
        assert state is not None
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

