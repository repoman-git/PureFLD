"""
Hurst-ETF Strategy

Applies J.M. Hurst cycle analysis to ETF trading.
Uses phasing, VTL construction, and VTL breaks for signals.

Works beautifully on cyclical assets: GLD, SLV, TLT, SPY, QQQ
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from meridian_v2_1_2.hurst import (
    HurstPhasingEngine,
    HurstVTLBuilder,
    HurstVTLBreakDetector
)


class HurstETF:
    """
    Hurst cycle analysis strategy for ETFs.
    
    Uses multi-timeframe cycle analysis:
    - Detects cycle troughs across multiple periods
    - Constructs Valid Trend Lines (VTL)
    - Generates signals on VTL breaks
    - Confirms with phase alignment
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize Hurst-ETF strategy.
        
        Args:
            params: Dictionary with:
                - nominal_periods: List of cycle periods (default: [20, 40, 80])
                - smooth_factor: Smoothing factor (default: 0.5)
                - allow_short: Enable short positions (default: False)
                - phase_threshold: Min phase for entry (default: 0.2)
                - stop_loss: Stop loss % (optional)
                - take_profit: Take profit % (optional)
        """
        self.nominal_periods = params.get("nominal_periods", [20, 40, 80])
        self.smooth_factor = params.get("smooth_factor", 0.5)
        self.allow_short = params.get("allow_short", False)
        self.phase_threshold = params.get("phase_threshold", 0.2)
        self.stop_loss = params.get("stop_loss", None)
        self.take_profit = params.get("take_profit", None)
        
        self.name = "Hurst-ETF"
        self.params = params
        
        # Initialize Hurst engines
        self.phasing_engine = HurstPhasingEngine(
            nominal_periods=self.nominal_periods,
            smooth_factor=self.smooth_factor
        )
        self.vtl_builder = HurstVTLBuilder()
        self.break_detector = HurstVTLBreakDetector()
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate Hurst cycle trading signals.
        
        Args:
            df: DataFrame with 'close' column
        
        Returns:
            DataFrame with added signal columns
        """
        df = df.copy()
        
        # Use close price for analysis
        price = df['close']
        
        # Phase all cycles
        all_phases = self.phasing_engine.phase_all(price)
        
        # Use primary cycle (shortest period)
        primary_period = self.nominal_periods[0]
        primary_cycle = all_phases[primary_period]
        
        # Get troughs and build VTL
        troughs = primary_cycle['troughs']
        vtl = self.vtl_builder.build_vtl(price, troughs)
        
        # Detect VTL breaks
        uptrend_breaks = self.break_detector.find_breaks(price, vtl, direction="uptrend")
        downtrend_breaks = self.break_detector.find_breaks(price, vtl, direction="downtrend")
        
        # Initialize signal columns
        df['long_signal'] = 0
        df['short_signal'] = 0
        df['hurst_phase'] = primary_cycle['phase']
        df['hurst_vtl'] = vtl
        
        # Generate signals based on VTL breaks and phase
        for idx in df.index:
            phase_value = df.loc[idx, 'hurst_phase']
            
            if pd.isna(phase_value):
                continue
            
            # Long signal: VTL break down (price crosses below VTL) in low phase
            # This indicates cycle trough - buy opportunity
            if idx in uptrend_breaks and phase_value < self.phase_threshold:
                df.loc[idx, 'long_signal'] = 1
            
            # Short signal: VTL break up (price crosses above VTL) in high phase
            # This indicates cycle peak - sell opportunity
            if self.allow_short:
                if idx in downtrend_breaks and phase_value > (1 - self.phase_threshold):
                    df.loc[idx, 'short_signal'] = 1
        
        # Calculate signal strength based on phase position
        df['signal_strength'] = 0.0
        
        # For long signals: stronger when phase is lower (closer to trough)
        long_mask = df['long_signal'] == 1
        df.loc[long_mask, 'signal_strength'] = 1.0 - df.loc[long_mask, 'hurst_phase']
        
        # For short signals: stronger when phase is higher (closer to peak)
        if self.allow_short:
            short_mask = df['short_signal'] == 1
            df.loc[short_mask, 'signal_strength'] = df.loc[short_mask, 'hurst_phase']
        
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
                        # Exit long
                        pnl = (current_price - entry_price) / entry_price
                        equity.append(prev_equity * (1 + pnl))
                        trades.append({'type': 'exit_long', 'price': current_price, 'pnl': pnl})
                        position = 0
                        continue
            
            # Entry logic
            if position == 0:
                # Long entry
                if df.iloc[i]['long_signal'] == 1:
                    position = 1
                    entry_price = current_price
                    trades.append({'type': 'enter_long', 'price': current_price})
                
                # Short entry
                elif self.allow_short and df.iloc[i]['short_signal'] == 1:
                    position = -1
                    entry_price = current_price
                    trades.append({'type': 'enter_short', 'price': current_price})
            
            # Update equity
            if position == 1:
                equity.append(prev_equity * (current_price / df.iloc[i-1]['close']))
            elif position == -1:
                equity.append(prev_equity * (df.iloc[i-1]['close'] / current_price))
            else:
                equity.append(prev_equity)
        
        # Calculate metrics
        equity_series = pd.Series(equity)
        returns = equity_series.pct_change().dropna()
        
        total_return = (equity[-1] / initial_capital - 1) * 100
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        max_dd = ((equity_series / equity_series.cummax()) - 1).min() * 100
        
        return {
            'equity_curve': equity,
            'trades': trades,
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd,
            'num_trades': len(trades),
            'final_equity': equity[-1]
        }

