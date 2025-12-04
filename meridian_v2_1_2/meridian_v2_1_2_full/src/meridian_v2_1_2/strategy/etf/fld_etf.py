"""
FLD-ETF Strategy

Applies Future Line of Demarcation (FLD) cycle analysis to ETFs.
Works beautifully on GLD, SLV, TLT, SPY, QQQ.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class FLD_ETF:
    """
    FLD strategy adapted for ETF trading.
    
    Uses cycle-based projection to identify trend changes.
    Particularly effective on gold (GLD), bonds (TLT), and equity (SPY/QQQ) ETFs.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize FLD-ETF strategy.
        
        Args:
            params: Dictionary with:
                - cycle: Cycle length (default: 20)
                - displacement: FLD displacement (default: 10)
                - allow_short: Enable short positions (default: False)
                - stop_loss: Stop loss % (optional)
                - take_profit: Take profit % (optional)
        """
        self.cycle = params.get("cycle", 20)
        self.displacement = params.get("displacement", 10)
        self.allow_short = params.get("allow_short", False)
        self.stop_loss = params.get("stop_loss", None)
        self.take_profit = params.get("take_profit", None)
        
        self.name = "FLD-ETF"
        self.params = params
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate FLD trading signals.
        
        Args:
            df: DataFrame with 'close' column
        
        Returns:
            DataFrame with added 'long_signal' and 'short_signal' columns
        """
        df = df.copy()
        
        # Calculate FLD: displaced moving average
        df["fld"] = df["close"].shift(self.displacement).rolling(self.cycle).mean()
        
        # Generate signals
        df["long_signal"] = (df["close"] > df["fld"]).astype(int)
        
        if self.allow_short:
            df["short_signal"] = (df["close"] < df["fld"]).astype(int)
        else:
            df["short_signal"] = 0
        
        # Add signal strength (distance from FLD)
        df["signal_strength"] = (df["close"] - df["fld"]) / df["fld"]
        
        return df
    
    def backtest(self, df: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """
        Run backtest on ETF data.
        
        Args:
            df: DataFrame with OHLCV data
            initial_capital: Starting capital
        
        Returns:
            Dictionary with equity curve, trades, and metrics
        """
        df = self.generate_signals(df)
        
        equity = [initial_capital]
        position = 0  # 0 = flat, 1 = long, -1 = short
        trades = []
        entry_price = 0
        
        for i in range(1, len(df)):
            current_price = df.iloc[i]['close']
            prev_equity = equity[-1]
            
            # Exit logic
            if position != 0:
                # Stop loss
                if self.stop_loss:
                    if position == 1 and current_price < entry_price * (1 - self.stop_loss):
                        # Exit long
                        pnl = (current_price - entry_price) / entry_price
                        equity.append(prev_equity * (1 + pnl))
                        trades.append({'type': 'exit_long', 'price': current_price, 'pnl': pnl})
                        position = 0
                        continue
                
                # Take profit
                if self.take_profit:
                    if position == 1 and current_price > entry_price * (1 + self.take_profit):
                        pnl = (current_price - entry_price) / entry_price
                        equity.append(prev_equity * (1 + pnl))
                        trades.append({'type': 'exit_long', 'price': current_price, 'pnl': pnl})
                        position = 0
                        continue
            
            # Entry logic
            if df.iloc[i]['long_signal'] == 1 and position == 0:
                position = 1
                entry_price = current_price
                trades.append({'type': 'enter_long', 'price': current_price})
                equity.append(prev_equity)
            
            elif df.iloc[i]['short_signal'] == 1 and position == 0 and self.allow_short:
                position = -1
                entry_price = current_price
                trades.append({'type': 'enter_short', 'price': current_price})
                equity.append(prev_equity)
            
            elif df.iloc[i]['long_signal'] == 0 and position == 1:
                # Exit long
                pnl = (current_price - entry_price) / entry_price
                equity.append(prev_equity * (1 + pnl))
                trades.append({'type': 'exit_long', 'price': current_price, 'pnl': pnl})
                position = 0
            
            elif df.iloc[i]['short_signal'] == 0 and position == -1:
                # Exit short
                pnl = (entry_price - current_price) / entry_price
                equity.append(prev_equity * (1 + pnl))
                trades.append({'type': 'exit_short', 'price': current_price, 'pnl': pnl})
                position = 0
            
            else:
                equity.append(prev_equity)
        
        return {
            'equity_curve': equity,
            'trades': trades,
            'final_equity': equity[-1],
            'total_return': (equity[-1] - initial_capital) / initial_capital,
            'num_trades': len([t for t in trades if 'enter' in t['type']])
        }
    
    def get_param_space(self) -> Dict[str, Any]:
        """Get parameter space for evolution/RL"""
        return {
            'cycle': (10, 60),
            'displacement': (5, 30),
            'allow_short': [True, False],
            'stop_loss': (0.02, 0.10),
            'take_profit': (0.05, 0.30)
        }


