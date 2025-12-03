"""
Local SQLite Database for Meridian v2.1.2

Persistent state storage with auto-migration.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class LocalDB:
    """
    Local SQLite database for Meridian state.
    
    Stores:
    - Strategy state
    - Portfolio positions
    - Orders and fills
    - Execution logs
    - Daily PnL
    - Risk metrics
    - WFA results
    - Incubation state
    - Regime/cycle history
    """
    
    def __init__(self, db_path: str = "meridian_local/meridian.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self._connect()
        self._init_schema()
    
    def _connect(self):
        """Connect to database with WAL mode"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.commit()
    
    def _init_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Strategy state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                date TEXT NOT NULL,
                params TEXT,
                weights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, date)
            )
        """)
        
        # Portfolio state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                qty REAL,
                cost_basis REAL,
                market_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                qty REAL NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT,
                status TEXT,
                submitted_at TIMESTAMP,
                filled_at TIMESTAMP
            )
        """)
        
        # Fills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL,
                filled_at TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)
        
        # Execution logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                log_type TEXT,
                message TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily PnL
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pnl_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                realized_pnl REAL,
                unrealized_pnl REAL,
                total_pnl REAL,
                equity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Risk metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                sharpe REAL,
                max_drawdown REAL,
                var_95 REAL,
                volatility REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # WFA results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wfa_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT NOT NULL,
                window_id INTEGER,
                train_sharpe REAL,
                oos_sharpe REAL,
                overfit_ratio REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Incubation state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incubation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                days_in_state INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Regime history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regime_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                regime_type TEXT NOT NULL,
                regime_label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cycle history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cycle_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                cycle_phase REAL,
                cycle_amplitude REAL,
                dominant_period INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute query"""
        return self.conn.execute(query, params)
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def init_database(db_path: str = "meridian_local/meridian.db") -> LocalDB:
    """
    Initialize local database.
    
    Args:
        db_path: Path to database file
    
    Returns:
        LocalDB instance
    """
    return LocalDB(db_path)

