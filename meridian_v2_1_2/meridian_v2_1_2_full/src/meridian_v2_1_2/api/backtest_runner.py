"""
Backtest Runner API

Clean wrapper around the Meridian backtester for notebook and dashboard use.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import uuid

from meridian_v2_1_2.config import MeridianConfig, StrategyConfig, SyntheticConfig
from meridian_v2_1_2.synthetic import SyntheticDataset
from meridian_v2_1_2.fld_engine import FLDCalculator
from meridian_v2_1_2.strategy import FLDStrategy
from meridian_v2_1_2.metrics_engine import MetricsEngine


@dataclass
class BacktestResult:
    """Container for backtest results"""
    run_id: str
    timestamp: str
    strategy_name: str
    params: Dict[str, Any]
    equity_curve: List[float]
    trades: List[Dict[str, Any]]
    metrics: Dict[str, float]
    logs: List[str]
    success: bool
    error: str = None
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return asdict(self)


def run_backtest(
    strategy_name: str = "FLD",
    params: Dict[str, Any] = None,
    start_date: str = None,
    end_date: str = None,
    initial_capital: float = 100000.0
) -> BacktestResult:
    """
    Run a backtest using the Meridian backtester.
    
    Args:
        strategy_name: Name of strategy to run (currently only "FLD" supported)
        params: Strategy parameters (e.g., fld_offset, cot_threshold, etc.)
        start_date: Start date for backtest (YYYY-MM-DD)
        end_date: End date for backtest (YYYY-MM-DD)
        initial_capital: Starting capital
    
    Returns:
        BacktestResult: Complete backtest results
    """
    
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    logs = []
    
    try:
        logs.append(f"Starting backtest: {strategy_name}")
        logs.append(f"Run ID: {run_id}")
        logs.append(f"Timestamp: {timestamp}")
        
        # Initialize configuration
        config = MeridianConfig()
        
        # Apply custom parameters if provided
        if params:
            logs.append(f"Applying custom parameters: {params}")
            for key, value in params.items():
                if hasattr(config.strategy, key):
                    setattr(config.strategy, key, value)
                    logs.append(f"  Set {key} = {value}")
        
        # Generate synthetic data
        logs.append("Generating synthetic data...")
        synthetic_config = SyntheticConfig(
            start_date=start_date or "2020-01-01",
            end_date=end_date or "2023-12-31",
            initial_price=1800.0
        )
        dataset = SyntheticDataset(synthetic_config)
        prices = dataset.generate_price_series()
        cot_data = dataset.generate_cot()
        seasonal_score = dataset.generate_seasonal_score()
        
        logs.append(f"Generated {len(prices)} price bars")
        
        # Initialize strategy components
        logs.append("Initializing strategy components...")
        fld_calc = FLDCalculator(config.fld)
        fld_result = fld_calc.calculate(prices['close'])
        
        strategy = FLDStrategy(config.strategy)
        signals_df = strategy.generate_signals(
            prices=prices['close'],
            fld=fld_result,
            cot_series=cot_data,
            seasonal_score=seasonal_score
        )
        
        logs.append(f"Generated {len(signals_df)} signals")
        
        # Simulate trading
        logs.append("Simulating trades...")
        positions = signals_df['signal'].shift(1).fillna(0)
        returns = prices['close'].pct_change()
        strategy_returns = positions * returns
        
        # Calculate equity curve
        equity = initial_capital * (1 + strategy_returns).cumprod()
        equity_curve = equity.fillna(initial_capital).tolist()
        
        # Extract trades
        trades = []
        position_changes = positions.diff()
        for idx, change in position_changes[position_changes != 0].items():
            if pd.notna(change):
                trades.append({
                    'date': str(idx),
                    'action': 'BUY' if change > 0 else 'SELL',
                    'position': float(positions.loc[idx]),
                    'price': float(prices.loc[idx, 'close']),
                    'equity': float(equity.loc[idx])
                })
        
        logs.append(f"Executed {len(trades)} trades")
        
        # Calculate metrics
        logs.append("Computing performance metrics...")
        metrics_engine = MetricsEngine()
        metrics_result = metrics_engine.calculate_metrics(strategy_returns)
        
        # Convert metrics to simple dict
        metrics = {
            'total_return': float(metrics_result.get('total_return', 0)),
            'sharpe_ratio': float(metrics_result.get('sharpe_ratio', 0)),
            'max_drawdown': float(metrics_result.get('max_drawdown', 0)),
            'win_rate': float(metrics_result.get('win_rate', 0)),
            'num_trades': len(trades),
            'final_equity': float(equity_curve[-1]) if equity_curve else initial_capital,
            'profit_factor': float(metrics_result.get('profit_factor', 0))
        }
        
        logs.append("Backtest completed successfully!")
        
        return BacktestResult(
            run_id=run_id,
            timestamp=timestamp,
            strategy_name=strategy_name,
            params=params or {},
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            logs=logs,
            success=True
        )
        
    except Exception as e:
        error_msg = f"Backtest failed: {str(e)}"
        logs.append(error_msg)
        
        return BacktestResult(
            run_id=run_id,
            timestamp=timestamp,
            strategy_name=strategy_name,
            params=params or {},
            equity_curve=[initial_capital],
            trades=[],
            metrics={},
            logs=logs,
            success=False,
            error=error_msg
        )


def quick_backtest(fld_offset: int = 10, cot_threshold: float = 0.0) -> BacktestResult:
    """
    Run a quick backtest with minimal parameters.
    
    Convenience function for notebook use.
    """
    params = {
        'fld_offset': fld_offset,
        'cot_threshold': cot_threshold
    }
    return run_backtest(strategy_name="FLD", params=params)

