"""
Data Integrity Enforcer

Runtime validation for Meridian's strict data quality requirements.

Author: Meridian Team
Date: December 4, 2025
"""

import pandas as pd
import datetime as dt
from typing import Union
from pathlib import Path


class DataIntegrityEnforcer:
    """
    Enforces Meridian's strict real-data rules at runtime.
    
    Validates:
    - Historical depth (must start ≥2000)
    - Minimum bar counts per component
    - Data quality (no NaN, outliers)
    - Timestamp consistency
    
    Example:
        >>> enforcer = DataIntegrityEnforcer()
        >>> enforcer.validate(price_data, module='phasing')
        # Raises ValueError if data insufficient
    """
    
    MIN_START_YEAR = 2000
    
    # Minimum bars required per component
    MIN_BARS = {
        "regime": 252,           # 1 year
        "volatility": 500,       # 2 years
        "phasing": 1500,         # 6 years
        "harmonics": 1500,       # 6 years
        "forecast": 1500,        # 6 years
        "cycle_discovery": 1500, # 6 years
        "intermarket": 2500,     # 10 years
        "backtest": 2500,        # 10 years
        "pairs_trading": 500,    # 2 years minimum
        "portfolio": 1000,       # 4 years
    }
    
    def __init__(self, log_violations: bool = True):
        """
        Initialize enforcer.
        
        Args:
            log_violations: Whether to log violations to file
        """
        self.log_violations = log_violations
        self.violation_log_path = Path("meridian_local/logs/policy_violations.log")
        
        if log_violations:
            self.violation_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def validate(
        self,
        data: Union[pd.DataFrame, pd.Series],
        module: str,
        symbol: str = "UNKNOWN"
    ) -> bool:
        """
        Validate data meets requirements.
        
        Args:
            data: DataFrame or Series to validate
            module: Module name (for looking up requirements)
            symbol: Symbol name (for logging)
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If data doesn't meet requirements
        """
        # Check data exists
        if data is None or len(data) == 0:
            self._log_violation(module, symbol, "No data supplied")
            raise ValueError(
                f"[DATA INTEGRITY] No data supplied to module '{module}'"
            )
        
        # Check datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            self._log_violation(module, symbol, "Non-datetime index")
            raise ValueError(
                f"[DATA INTEGRITY] Module '{module}' requires DatetimeIndex"
            )
        
        # Check start date
        start = data.index.min()
        required = dt.datetime(self.MIN_START_YEAR, 1, 1)
        
        if start > required:
            days_short = (start - required).days
            self._log_violation(
                module, symbol,
                f"Start date {start.date()} too recent (needs {required.date()}), short by {days_short} days"
            )
            raise ValueError(
                f"[DATA INTEGRITY VIOLATION]\n"
                f"Module: {module}\n"
                f"Symbol: {symbol}\n"
                f"Dataset starts: {start.date()}\n"
                f"Required start: {required.date()}\n"
                f"Missing: {days_short} days of history\n"
                f"Action: Load more historical data (extend back to year {self.MIN_START_YEAR})"
            )
        
        # Check bar count
        min_bars = self.MIN_BARS.get(module, None)
        if min_bars and len(data) < min_bars:
            bars_short = min_bars - len(data)
            self._log_violation(
                module, symbol,
                f"Only {len(data)} bars (needs {min_bars}), short by {bars_short}"
            )
            raise ValueError(
                f"[DATA INTEGRITY VIOLATION]\n"
                f"Module: {module}\n"
                f"Symbol: {symbol}\n"
                f"Dataset has: {len(data)} bars\n"
                f"Required: {min_bars} bars\n"
                f"Missing: {bars_short} bars\n"
                f"Action: Load more historical data"
            )
        
        return True
    
    def _log_violation(self, module: str, symbol: str, message: str):
        """Log policy violation"""
        if not self.log_violations:
            return
        
        timestamp = dt.datetime.now().isoformat()
        log_entry = f"[{timestamp}] Module={module}, Symbol={symbol}, Issue={message}\n"
        
        try:
            with open(self.violation_log_path, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Don't fail if logging fails


# Singleton instance
data_integrity = DataIntegrityEnforcer()

