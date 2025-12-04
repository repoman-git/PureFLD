"""
Pairs Backtesting Engine

Realistic backtesting for pairs trading strategies with transaction costs,
slippage, and position management.

Features:
- Realistic execution with slippage
- Transaction costs (commissions, spreads)
- Position sizing and risk management
- Portfolio tracking (equity curve, drawdowns)
- Trade-by-trade analytics
- Performance metrics (Sharpe, Sortino, Calmar)

Execution Model:
- Market orders with slippage
- Realistic fill prices
- Separate tracking for lead and lag legs
- Portfolio rebalancing
- Risk limits

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from .pairs_strategy import PairsStrategy, PairsSignal, SignalType
from .pairs_selector import PairCandidate


@dataclass
class TradeResult:
    """Container for a completed trade"""
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    lead_asset: str
    lag_asset: str
    entry_spread: float
    exit_spread: float
    lead_entry: float
    lead_exit: float
    lag_entry: float
    lag_exit: float
    lead_position: float
    lag_position: float
    pnl_gross: float
    pnl_net: float
    costs: float
    holding_days: int
    exit_reason: str
    
    def __repr__(self):
        return (f"Trade({self.lead_asset}/{self.lag_asset}, "
                f"{self.holding_days}d, PnL={self.pnl_net:.2%})")


@dataclass
class BacktestResult:
    """Container for backtest results"""
    trades: List[TradeResult] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series())
    daily_returns: pd.Series = field(default_factory=lambda: pd.Series())
    
    # Performance metrics
    total_return: float = 0.0
    annual_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    calmar_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_trade_pnl: float = 0.0
    total_trades: int = 0
    
    def summary(self) -> Dict:
        """Get summary statistics"""
        return {
            'Total Return': f"{self.total_return:.2%}",
            'Annual Return': f"{self.annual_return:.2%}",
            'Sharpe Ratio': f"{self.sharpe_ratio:.2f}",
            'Sortino Ratio': f"{self.sortino_ratio:.2f}",
            'Max Drawdown': f"{self.max_drawdown:.2%}",
            'Calmar Ratio': f"{self.calmar_ratio:.2f}",
            'Win Rate': f"{self.win_rate:.2%}",
            'Profit Factor': f"{self.profit_factor:.2f}",
            'Total Trades': self.total_trades,
            'Avg Trade PnL': f"{self.avg_trade_pnl:.2%}"
        }


class PairsBacktester:
    """
    Backtester for pairs trading strategies.
    
    Simulates realistic execution of pairs trades including:
    - Transaction costs
    - Slippage
    - Position sizing
    - Risk management
    - Portfolio tracking
    
    Example:
        >>> backtester = PairsBacktester(
        ...     initial_capital=100000,
        ...     commission=0.001,
        ...     slippage=0.0005
        ... )
        >>> 
        >>> result = backtester.backtest(
        ...     pair_candidate=pair,
        ...     strategy=strategy,
        ...     lead_prices=gold_prices,
        ...     lag_prices=silver_prices
        ... )
        >>> 
        >>> print(result.summary())
        >>> print(f"Sharpe: {result.sharpe_ratio:.2f}")
    """
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 10 bps per side
        slippage: float = 0.0005,   # 5 bps slippage
        risk_per_trade: float = 0.02,  # 2% risk per trade
        max_position_size: float = 0.25,  # 25% max per instrument
        risk_free_rate: float = 0.02  # 2% for Sharpe calculation
    ):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade (e.g., 0.001 = 0.1%)
            slippage: Slippage rate per trade
            risk_per_trade: Fraction of capital to risk per trade
            max_position_size: Maximum position size per instrument
            risk_free_rate: Risk-free rate for Sharpe ratio
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.risk_free_rate = risk_free_rate
    
    def backtest(
        self,
        pair_candidate: PairCandidate,
        strategy: PairsStrategy,
        lead_prices: pd.Series,
        lag_prices: pd.Series,
        start_date: Optional[pd.Timestamp] = None,
        end_date: Optional[pd.Timestamp] = None
    ) -> BacktestResult:
        """
        Run backtest for a pairs strategy.
        
        Args:
            pair_candidate: Pair definition
            strategy: Trading strategy
            lead_prices: Historical prices for lead asset
            lag_prices: Historical prices for lag asset
            start_date: Start of backtest period
            end_date: End of backtest period
            
        Returns:
            BacktestResult with performance metrics
        """
        # Filter date range
        if start_date:
            lead_prices = lead_prices.loc[start_date:]
            lag_prices = lag_prices.loc[start_date:]
        if end_date:
            lead_prices = lead_prices.loc[:end_date]
            lag_prices = lag_prices.loc[:end_date]
        
        # Generate trading signals
        signals = strategy.generate_signals(
            pair_candidate=pair_candidate,
            lead_prices=lead_prices,
            lag_prices=lag_prices
        )
        
        if not signals:
            return BacktestResult()
        
        # Simulate trading
        trades = self._simulate_trades(
            signals=signals,
            lead_prices=lead_prices,
            lag_prices=lag_prices,
            spread_volatility=pair_candidate.spread_volatility
        )
        
        # Compute equity curve
        equity_curve = self._compute_equity_curve(
            trades=trades,
            lead_prices=lead_prices,
            lag_prices=lag_prices
        )
        
        # Compute returns
        daily_returns = equity_curve.pct_change().fillna(0)
        
        # Compute performance metrics
        result = BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            daily_returns=daily_returns
        )
        
        self._compute_metrics(result)
        
        return result
    
    def _simulate_trades(
        self,
        signals: List[PairsSignal],
        lead_prices: pd.Series,
        lag_prices: pd.Series,
        spread_volatility: float
    ) -> List[TradeResult]:
        """
        Simulate execution of all trades.
        """
        trades = []
        open_trade = None
        
        for signal in signals:
            if 'ENTRY' in signal.signal_type.value:
                # Open new trade
                open_trade = self._open_trade(signal)
                
            elif 'EXIT' in signal.signal_type.value and open_trade:
                # Close existing trade
                trade_result = self._close_trade(open_trade, signal)
                if trade_result:
                    trades.append(trade_result)
                open_trade = None
        
        return trades
    
    def _open_trade(self, signal: PairsSignal) -> Dict:
        """
        Open a new trade (entry signal).
        """
        # Apply slippage and commission
        lead_fill = signal.entry_price_lead * (1 + signal.lead_position * self.slippage)
        lag_fill = signal.entry_price_lag * (1 + signal.lag_position * self.slippage)
        
        # Compute position sizes (dollar amounts)
        capital = self.initial_capital  # Simplified: use initial capital
        position_size = capital * self.risk_per_trade * signal.confidence
        
        # Split between lead and lag
        lead_dollar = position_size / 2.0
        lag_dollar = position_size / 2.0
        
        # Compute shares (for tracking)
        lead_shares = lead_dollar / lead_fill
        lag_shares = lag_dollar / lag_fill
        
        return {
            'entry_signal': signal,
            'entry_date': signal.timestamp,
            'lead_entry_price': lead_fill,
            'lag_entry_price': lag_fill,
            'lead_shares': lead_shares * signal.lead_position,
            'lag_shares': lag_shares * signal.lag_position,
            'lead_dollar': lead_dollar * abs(signal.lead_position),
            'lag_dollar': lag_dollar * abs(signal.lag_position)
        }
    
    def _close_trade(self, open_trade: Dict, exit_signal: PairsSignal) -> Optional[TradeResult]:
        """
        Close an existing trade (exit signal).
        """
        entry_signal = open_trade['entry_signal']
        
        # Apply slippage to exit prices
        lead_exit_price = exit_signal.exit_price_lead * (1 - entry_signal.lead_position * self.slippage)
        lag_exit_price = exit_signal.exit_price_lag * (1 - entry_signal.lag_position * self.slippage)
        
        # Compute P&L for each leg
        lead_pnl_gross = open_trade['lead_shares'] * (
            lead_exit_price - open_trade['lead_entry_price']
        )
        lag_pnl_gross = open_trade['lag_shares'] * (
            lag_exit_price - open_trade['lag_entry_price']
        )
        
        total_pnl_gross = lead_pnl_gross + lag_pnl_gross
        
        # Compute transaction costs
        # Entry: 2 legs × 2 sides (buy+sell) × commission
        # Exit: same
        total_notional = open_trade['lead_dollar'] + open_trade['lag_dollar']
        entry_costs = total_notional * self.commission * 2  # 2 legs
        exit_costs = total_notional * self.commission * 2   # 2 legs
        total_costs = entry_costs + exit_costs
        
        # Net P&L
        total_pnl_net = total_pnl_gross - total_costs
        
        # Holding period
        holding_days = (exit_signal.timestamp - open_trade['entry_date']).days
        
        # Exit reason
        exit_reason = exit_signal.signal_type.value
        
        return TradeResult(
            entry_date=open_trade['entry_date'],
            exit_date=exit_signal.timestamp,
            lead_asset=entry_signal.lead_asset,
            lag_asset=entry_signal.lag_asset,
            entry_spread=entry_signal.spread_value,
            exit_spread=exit_signal.spread_value,
            lead_entry=open_trade['lead_entry_price'],
            lead_exit=lead_exit_price,
            lag_entry=open_trade['lag_entry_price'],
            lag_exit=lag_exit_price,
            lead_position=entry_signal.lead_position,
            lag_position=entry_signal.lag_position,
            pnl_gross=total_pnl_gross,
            pnl_net=total_pnl_net,
            costs=total_costs,
            holding_days=holding_days,
            exit_reason=exit_reason
        )
    
    def _compute_equity_curve(
        self,
        trades: List[TradeResult],
        lead_prices: pd.Series,
        lag_prices: pd.Series
    ) -> pd.Series:
        """
        Compute daily equity curve from trades.
        """
        # Get date range
        if not trades:
            return pd.Series([self.initial_capital], index=[lead_prices.index[0]])
        
        all_dates = lead_prices.index
        equity = pd.Series(self.initial_capital, index=all_dates)
        
        # Apply trade results at exit dates
        cumulative_pnl = 0.0
        for trade in trades:
            cumulative_pnl += trade.pnl_net
            # Update equity from exit date onward
            mask = equity.index >= trade.exit_date
            equity.loc[mask] = self.initial_capital + cumulative_pnl
        
        return equity
    
    def _compute_metrics(self, result: BacktestResult):
        """
        Compute all performance metrics and update result object.
        """
        if not result.trades:
            return
        
        # Basic trade statistics
        result.total_trades = len(result.trades)
        
        pnls = [t.pnl_net for t in result.trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        result.win_rate = len(wins) / len(pnls) if pnls else 0.0
        result.avg_trade_pnl = np.mean(pnls) / self.initial_capital if pnls else 0.0
        
        if losses and sum(losses) != 0:
            result.profit_factor = abs(sum(wins) / sum(losses))
        else:
            result.profit_factor = np.inf if wins else 0.0
        
        # Equity curve metrics
        equity = result.equity_curve
        if len(equity) > 0:
            result.total_return = (equity.iloc[-1] - self.initial_capital) / self.initial_capital
            
            # Annualized return
            years = len(equity) / 252  # Trading days
            if years > 0:
                result.annual_return = (1 + result.total_return) ** (1 / years) - 1
            
            # Max drawdown
            peak = equity.expanding().max()
            drawdown = (equity - peak) / peak
            result.max_drawdown = abs(drawdown.min())
            
            # Calmar ratio
            if result.max_drawdown != 0:
                result.calmar_ratio = result.annual_return / result.max_drawdown
        
        # Sharpe and Sortino ratios
        returns = result.daily_returns
        if len(returns) > 1:
            excess_returns = returns - self.risk_free_rate / 252
            
            if excess_returns.std() != 0:
                result.sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
            
            # Sortino (downside deviation)
            downside = excess_returns[excess_returns < 0]
            if len(downside) > 0 and downside.std() != 0:
                result.sortino_ratio = np.sqrt(252) * excess_returns.mean() / downside.std()
    
    def plot_results(self, result: BacktestResult) -> Dict:
        """
        Generate plot data for backtest visualization.
        
        Returns:
            Dictionary with plot data
        """
        equity = result.equity_curve
        
        # Drawdown
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        
        # Trade markers
        entry_dates = [t.entry_date for t in result.trades]
        entry_equity = [equity.loc[t.entry_date] if t.entry_date in equity.index else None 
                       for t in result.trades]
        exit_dates = [t.exit_date for t in result.trades]
        exit_equity = [equity.loc[t.exit_date] if t.exit_date in equity.index else None
                      for t in result.trades]
        
        return {
            'dates': equity.index,
            'equity': equity.values,
            'drawdown': drawdown.values,
            'entry_dates': entry_dates,
            'entry_equity': entry_equity,
            'exit_dates': exit_dates,
            'exit_equity': exit_equity,
            'initial_capital': self.initial_capital
        }

