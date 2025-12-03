"""
Backtester Engine for Meridian v2.1.2

Deterministic, vectorized backtest execution with position tracking and PnL calculation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BacktestConfig:
    """Backtesting parameters"""
    initial_capital: float = 100000.0
    commission: float = 0.0          # Per contract per trade
    slippage: float = 0.0            # Per contract per trade
    contract_size: float = 1.0       # Multiplier for P&L
    contracts: int = 1               # Number of contracts per position


class Backtester:
    """
    Deterministic backtesting engine for strategy evaluation.
    
    Features:
    - Vectorized PnL calculation
    - Commission and slippage modeling
    - Equity curve generation
    - Trade-level statistics
    - No hidden state or randomness
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
    
    def run(
        self,
        prices: pd.Series,
        positions: pd.Series
    ) -> Dict[str, Any]:
        """
        Execute backtest on price and position series.
        
        Args:
            prices: Price series with DatetimeIndex
            positions: Position series (+1=long, -1=short, 0=flat)
                      Must have same index as prices
        
        Returns:
            Dictionary containing:
                - 'equity': Equity curve series
                - 'returns': Per-bar returns series
                - 'trades': DataFrame of individual trades
                - 'stats': Dictionary of performance statistics
        
        Raises:
            ValueError: If indices don't match or inputs are invalid
        """
        # Validate inputs
        if not prices.index.equals(positions.index):
            raise ValueError("Price and position indices do not match")
        
        if len(prices) == 0:
            raise ValueError("Price series is empty")
        
        # Initialize equity curve
        equity = pd.Series(self.config.initial_capital, index=prices.index)
        returns = pd.Series(0.0, index=prices.index)
        
        # Detect position changes
        position_changes = positions.diff()
        position_changes.iloc[0] = positions.iloc[0]  # First bar is a change if non-zero
        
        # Calculate PnL bar by bar
        running_capital = self.config.initial_capital
        
        for i in range(len(prices)):
            if i == 0:
                # First bar
                equity.iloc[i] = running_capital
                returns.iloc[i] = 0.0
                
                # Apply commission/slippage if entering position
                if positions.iloc[i] != 0:
                    cost = self._calculate_transaction_cost(positions.iloc[i])
                    running_capital -= cost
                    equity.iloc[i] = running_capital
            else:
                # Calculate PnL from position held
                prev_position = positions.iloc[i-1]
                price_change = prices.iloc[i] - prices.iloc[i-1]
                
                # PnL = position * price_change * contract_size * contracts
                pnl = prev_position * price_change * self.config.contract_size * self.config.contracts
                running_capital += pnl
                
                # Apply transaction costs if position changed
                if position_changes.iloc[i] != 0:
                    # Count transitions: flat->long (1), long->short (2), etc.
                    if prev_position == 0:
                        # Entering from flat
                        cost = self._calculate_transaction_cost(positions.iloc[i])
                    elif positions.iloc[i] == 0:
                        # Exiting to flat
                        cost = self._calculate_transaction_cost(prev_position)
                    else:
                        # Flipping position (e.g., long -> short)
                        cost = self._calculate_transaction_cost(prev_position)  # Exit old
                        cost += self._calculate_transaction_cost(positions.iloc[i])  # Enter new
                    
                    running_capital -= cost
                
                equity.iloc[i] = running_capital
                returns.iloc[i] = (equity.iloc[i] / equity.iloc[i-1]) - 1.0
        
        # Extract trades
        trades = self._extract_trades(prices, positions)
        
        # Calculate statistics
        stats = self._calculate_statistics(equity, returns, trades)
        
        return {
            'equity': equity,
            'returns': returns,
            'trades': trades,
            'stats': stats
        }
    
    def _calculate_transaction_cost(self, position: int) -> float:
        """
        Calculate total transaction cost for a position change.
        
        Args:
            position: Position size (can be negative for shorts)
        
        Returns:
            float: Total cost (commission + slippage) * contracts
        """
        if position == 0:
            return 0.0
        
        # Cost per contract
        cost_per_contract = self.config.commission + self.config.slippage
        
        # Total cost = cost per contract * number of contracts
        total_cost = cost_per_contract * self.config.contracts
        
        return abs(total_cost)  # Always positive cost
    
    def _extract_trades(
        self,
        prices: pd.Series,
        positions: pd.Series
    ) -> pd.DataFrame:
        """
        Extract individual trades from position series.
        
        A trade starts when position != 0 and ends when it returns to 0 or flips.
        
        Returns:
            DataFrame with columns: ['entry_date', 'exit_date', 'entry_price', 
                                     'exit_price', 'direction', 'pnl']
        """
        trades = []
        
        in_trade = False
        entry_idx = None
        entry_price = None
        entry_direction = None
        
        for i in range(len(positions)):
            curr_pos = positions.iloc[i]
            
            if not in_trade and curr_pos != 0:
                # Entering trade
                in_trade = True
                entry_idx = i
                entry_price = prices.iloc[i]
                entry_direction = 'long' if curr_pos > 0 else 'short'
            
            elif in_trade and (curr_pos == 0 or (i > entry_idx and np.sign(curr_pos) != np.sign(positions.iloc[entry_idx]))):
                # Exiting trade (to flat or flip)
                exit_price = prices.iloc[i-1]  # Exit at previous bar's close
                exit_idx = i - 1
                
                # Calculate PnL
                if entry_direction == 'long':
                    pnl = (exit_price - entry_price) * self.config.contract_size * self.config.contracts
                else:
                    pnl = (entry_price - exit_price) * self.config.contract_size * self.config.contracts
                
                # Subtract transaction costs
                entry_cost = self._calculate_transaction_cost(positions.iloc[entry_idx])
                exit_cost = self._calculate_transaction_cost(positions.iloc[entry_idx])
                pnl -= (entry_cost + exit_cost)
                
                trades.append({
                    'entry_date': positions.index[entry_idx],
                    'exit_date': positions.index[exit_idx],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'direction': entry_direction,
                    'pnl': pnl,
                    'bars': exit_idx - entry_idx + 1
                })
                
                # Check if flipping to opposite position
                if curr_pos != 0:
                    in_trade = True
                    entry_idx = i
                    entry_price = prices.iloc[i]
                    entry_direction = 'long' if curr_pos > 0 else 'short'
                else:
                    in_trade = False
        
        # Handle open trade at end
        if in_trade:
            exit_price = prices.iloc[-1]
            exit_idx = len(positions) - 1
            
            if entry_direction == 'long':
                pnl = (exit_price - entry_price) * self.config.contract_size * self.config.contracts
            else:
                pnl = (entry_price - exit_price) * self.config.contract_size * self.config.contracts
            
            entry_cost = self._calculate_transaction_cost(positions.iloc[entry_idx])
            pnl -= entry_cost
            
            trades.append({
                'entry_date': positions.index[entry_idx],
                'exit_date': positions.index[exit_idx],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'direction': entry_direction,
                'pnl': pnl,
                'bars': exit_idx - entry_idx + 1,
                'open': True
            })
        
        return pd.DataFrame(trades)
    
    def _calculate_statistics(
        self,
        equity: pd.Series,
        returns: pd.Series,
        trades: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculate performance statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            'initial_capital': self.config.initial_capital,
            'final_equity': equity.iloc[-1],
            'total_return': (equity.iloc[-1] / self.config.initial_capital) - 1.0,
            'total_trades': len(trades),
            'winning_trades': len(trades[trades['pnl'] > 0]) if len(trades) > 0 else 0,
            'losing_trades': len(trades[trades['pnl'] < 0]) if len(trades) > 0 else 0,
        }
        
        # Win rate
        if stats['total_trades'] > 0:
            stats['win_rate'] = stats['winning_trades'] / stats['total_trades']
        else:
            stats['win_rate'] = 0.0
        
        # Average trade PnL
        if len(trades) > 0:
            stats['avg_trade_pnl'] = trades['pnl'].mean()
            stats['total_pnl'] = trades['pnl'].sum()
        else:
            stats['avg_trade_pnl'] = 0.0
            stats['total_pnl'] = 0.0
        
        # Maximum drawdown
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        stats['max_drawdown'] = drawdown.min()
        
        return stats


def run_backtest(
    prices: pd.Series,
    positions: pd.Series,
    config: Optional[BacktestConfig] = None
) -> Dict[str, Any]:
    """
    Convenience function to run a backtest.
    
    Args:
        prices: Price series
        positions: Position series
        config: Backtest configuration (uses defaults if None)
    
    Returns:
        Backtest results dictionary
    """
    if config is None:
        config = BacktestConfig()
    
    backtester = Backtester(config)
    return backtester.run(prices, positions)
