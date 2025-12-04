"""Portfolio Backtest Engine"""
import pandas as pd
import numpy as np
from typing import Dict

class PortfolioBacktestEngine:
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
    
    def backtest(self, price_dict: Dict[str, pd.Series], weights: pd.DataFrame) -> pd.DataFrame:
        """Run portfolio backtest"""
        # Align prices
        df_price = pd.DataFrame(price_dict)
        returns = df_price.pct_change().fillna(0)
        
        # Align weights and returns
        common_idx = returns.index.intersection(weights.index)
        returns = returns.loc[common_idx]
        weights = weights.loc[common_idx]
        
        # Portfolio returns (lag weights by 1 period)
        portfolio_returns = (returns * weights.shift(1).fillna(0)).sum(axis=1)
        
        # Transaction costs
        weight_changes = weights.diff().abs().sum(axis=1)
        costs = weight_changes * self.commission
        portfolio_returns -= costs
        
        # Equity curve
        equity = self.initial_capital * (1 + portfolio_returns).cumprod()
        
        # Calculate metrics
        sharpe = np.sqrt(252) * portfolio_returns.mean() / (portfolio_returns.std() + 1e-10)
        max_dd = self._calculate_max_drawdown(equity)
        
        return pd.DataFrame({
            "portfolio_returns": portfolio_returns,
            "equity": equity,
            "sharpe": sharpe,
            "max_drawdown": max_dd
        })
    
    def _calculate_max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = equity.expanding().max()
        dd = (equity - peak) / peak
        return dd.min()

