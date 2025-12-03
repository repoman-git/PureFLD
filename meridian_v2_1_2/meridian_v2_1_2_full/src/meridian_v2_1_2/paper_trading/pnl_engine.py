"""
PnL Engine

Calculates realized/unrealized PnL and portfolio metrics.

⚠️  EDUCATIONAL METRICS ONLY - Not investment advice
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np


@dataclass
class PnLReport:
    """Portfolio PnL and metrics report"""
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    total_return_pct: float
    daily_return_pct: float
    cumulative_returns: List[float]
    max_drawdown: float
    volatility: float  # annualized
    sharpe_ratio: float
    
    # Educational disclaimers
    is_educational: bool = True
    disclaimer: str = "Educational metrics only - not investment advice"


class PnLEngine:
    """
    Calculates PnL and risk metrics for paper trading.
    
    ⚠️  ALL METRICS ARE EDUCATIONAL ONLY
    """
    
    def __init__(self):
        """Initialize PnL engine"""
        self.trade_history: List[Dict[str, Any]] = []
    
    def calculate_pnl(
        self,
        portfolio_state: Dict[str, Any],
        initial_capital: float
    ) -> PnLReport:
        """
        Calculate comprehensive PnL report.
        
        Args:
            portfolio_state: Current portfolio state
            initial_capital: Initial capital
        
        Returns:
            PnLReport with all metrics
        """
        # Get current values
        current_value = portfolio_state.get('total_value', initial_capital)
        cash = portfolio_state.get('cash', initial_capital)
        
        # Calculate unrealized PnL from positions
        unrealized_pnl = sum(
            pos.get('unrealized_pnl', 0)
            for pos in portfolio_state.get('positions', {}).values()
        )
        
        # Realized PnL (from closed trades)
        realized_pnl = current_value - initial_capital - unrealized_pnl
        
        # Total PnL
        total_pnl = current_value - initial_capital
        total_return_pct = (total_pnl / initial_capital) * 100
        
        # Value history for metrics
        value_history = portfolio_state.get('value_history', [])
        
        if len(value_history) > 1:
            returns = self._calculate_returns(value_history)
            max_dd = self._calculate_max_drawdown(value_history)
            vol = self._calculate_volatility(returns)
            sharpe = self._calculate_sharpe(returns, vol)
            daily_return = returns[-1] if returns else 0.0
        else:
            returns = [0.0]
            max_dd = 0.0
            vol = 0.0
            sharpe = 0.0
            daily_return = 0.0
        
        return PnLReport(
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=total_pnl,
            total_return_pct=total_return_pct,
            daily_return_pct=daily_return * 100,
            cumulative_returns=returns,
            max_drawdown=max_dd,
            volatility=vol,
            sharpe_ratio=sharpe
        )
    
    def _calculate_returns(self, value_history: List[Dict[str, Any]]) -> List[float]:
        """Calculate returns from value history"""
        if len(value_history) < 2:
            return [0.0]
        
        values = [v['total_value'] for v in value_history]
        returns = []
        
        for i in range(1, len(values)):
            ret = (values[i] / values[i-1]) - 1
            returns.append(ret)
        
        return returns
    
    def _calculate_max_drawdown(self, value_history: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown"""
        if len(value_history) < 2:
            return 0.0
        
        values = np.array([v['total_value'] for v in value_history])
        cummax = np.maximum.accumulate(values)
        drawdowns = (values - cummax) / cummax
        
        return float(abs(drawdowns.min()))
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate annualized volatility"""
        if len(returns) < 2:
            return 0.0
        
        daily_vol = np.std(returns)
        annual_vol = daily_vol * np.sqrt(252)  # 252 trading days
        
        return float(annual_vol)
    
    def _calculate_sharpe(self, returns: List[float], volatility: float) -> float:
        """
        Calculate Sharpe ratio.
        
        ⚠️  EDUCATIONAL ONLY - simplified calculation
        """
        if volatility == 0 or len(returns) < 2:
            return 0.0
        
        avg_return = np.mean(returns)
        annual_return = avg_return * 252
        
        # Assume 2% risk-free rate (educational assumption)
        risk_free_rate = 0.02
        
        sharpe = (annual_return - risk_free_rate) / volatility
        
        return float(sharpe)

