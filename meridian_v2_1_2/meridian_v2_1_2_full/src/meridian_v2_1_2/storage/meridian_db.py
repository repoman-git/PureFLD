"""Meridian Database Layer"""
import sqlite3
import pandas as pd
from pathlib import Path

class MeridianDB:
    """Persistent storage for all Meridian data"""
    
    def __init__(self, db_path: str = "meridian_local/meridian.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create core tables"""
        tables = {
            "signals": "CREATE TABLE IF NOT EXISTS signals (timestamp TEXT, symbol TEXT, signal REAL, confidence REAL)",
            "trades": "CREATE TABLE IF NOT EXISTS trades (timestamp TEXT, symbol TEXT, side TEXT, qty REAL, price REAL, status TEXT)",
            "forecasts": "CREATE TABLE IF NOT EXISTS forecasts (timestamp TEXT, symbol TEXT, forecast_value REAL, horizon INT)",
            "regimes": "CREATE TABLE IF NOT EXISTS regimes (timestamp TEXT, regime INT, confidence REAL)",
            "positions": "CREATE TABLE IF NOT EXISTS positions (timestamp TEXT, symbol TEXT, qty REAL, value REAL)"
        }
        for table_sql in tables.values():
            self.conn.execute(table_sql)
        self.conn.commit()
    
    def write(self, table: str, df: pd.DataFrame):
        """Write DataFrame to table"""
        df.to_sql(table, self.conn, if_exists="append", index=False)
    
    def read(self, query: str) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        return pd.read_sql_query(query, self.conn)
    
    def close(self):
        self.conn.close()

db = MeridianDB()

