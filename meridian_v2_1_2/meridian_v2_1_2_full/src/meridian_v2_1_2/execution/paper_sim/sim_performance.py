"""
Simulated Performance Tracker for Meridian v2.1.2

Track and compute performance metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict


class SimulatedPerformance:
    """
    Performance tracker for paper trading.
    
    Computes:
    - Daily PnL
    - Cumulative PnL
    - Drawdowns
    - Sharpe
    - Returns
    """
    
    def __init__(self):
        """Initialize performance tracker"""
        self.equity_history: List[float] = []
        self.dates: List[str] = []
        self.daily_returns: List[float] = []
    
    def update(self, date: str, equity: float) -> None:
        """
        Update with daily equity.
        
        Args:
            date: Date string
            equity: Total equity
        """
        self.dates.append(date)
        self.equity_history.append(equity)
        
        # Calculate return
        if len(self.equity_history) > 1:
            prev_equity = self.equity_history[-2]
            daily_return = (equity - prev_equity) / prev_equity if prev_equity > 0 else 0.0
            self.daily_returns.append(daily_return)
        else:
            self.daily_returns.append(0.0)
    
    def get_total_return(self) -> float:
        """Get total return"""
        if len(self.equity_history) < 2:
            return 0.0
        return (self.equity_history[-1] / self.equity_history[0]) - 1.0
    
    def get_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            risk_free_rate: Risk-free rate (annual)
        
        Returns:
            float: Sharpe ratio
        """
        if len(self.daily_returns) < 2:
            return 0.0
        
        returns = np.array(self.daily_returns)
        excess_returns = returns - (risk_free_rate / 252)
        
        if returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
    
    def get_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown.
        
        Returns:
            float: Max drawdown (negative)
        """
        if len(self.equity_history) < 2:
            return 0.0
        
        equity_series = pd.Series(self.equity_history)
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax
        
        return drawdown.min()
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get all performance metrics.
        
        Returns:
            Dict of metrics
        """
        return {
            'total_return': self.get_total_return(),
            'sharpe': self.get_sharpe_ratio(),
            'max_drawdown': self.get_max_drawdown(),
            'total_days': len(self.equity_history),
            'current_equity': self.equity_history[-1] if self.equity_history else 0.0
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Export to DataFrame.
        
        Returns:
            pd.DataFrame with performance history
        """
        return pd.DataFrame({
            'date': self.dates,
            'equity': self.equity_history,
            'return': self.daily_returns
        })


