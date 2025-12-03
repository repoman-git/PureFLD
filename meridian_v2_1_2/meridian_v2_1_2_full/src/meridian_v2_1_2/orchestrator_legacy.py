import pandas as pd
from typing import Optional, Dict, Any
from .config import MeridianConfig
from .seasonality import compute_tdom_flags, compute_tdoy_flags, combine_seasonal_flags
from .strategy import FLDStrategy, StrategyConfig
from .fld_engine import compute_fld
from .backtester import run_backtest as run_backtest_engine, BacktestConfig

def run_backtest(
    config: MeridianConfig,
    price_data: pd.Series,
    cot_data: Optional[pd.Series] = None
) -> Dict[str, Any]:
    """
    Execute full Meridian backtest workflow.
    
    Args:
        config: MeridianConfig object
        price_data: Price series with DatetimeIndex
        cot_data: Optional COT factor series
    
    Returns:
        Dictionary with results including signals, positions, and stats
    """
    # Step 1: Compute FLD
    fld = compute_fld(price_data, config.fld.cycle_length, config.fld.displacement)
    
    # Step 2: Compute seasonal flags
    tdom_series = None
    tdoy_series = None
    seasonal_score = None
    
    # Compute TDOM if enabled
    if config.seasonality.use_tdom:
        tdom_series = compute_tdom_flags(
            price_data.index,
            config.seasonality.favourable_days,
            config.seasonality.unfavourable_days
        )
    
    # Compute TDOY if enabled
    if config.seasonality.use_tdoy:
        tdoy_series = compute_tdoy_flags(
            price_data.index,
            config.seasonality.tdoy_favourable,
            config.seasonality.tdoy_unfavourable
        )
    
    # Combine seasonal flags into seasonal score
    if tdom_series is not None or tdoy_series is not None:
        if tdom_series is not None and tdoy_series is not None:
            seasonal_score = combine_seasonal_flags(tdom_series, tdoy_series)
        elif tdom_series is not None:
            seasonal_score = tdom_series
        else:
            seasonal_score = tdoy_series
    
    # Step 3: Generate signals via strategy
    strategy = FLDStrategy(config.strategy)
    signals_df = strategy.generate_signals(
        prices=price_data,
        fld=fld,
        cot_series=cot_data,
        seasonal_score=seasonal_score
    )
    
    # Step 4: Run backtester
    backtest_config = BacktestConfig(
        initial_capital=config.backtest.initial_capital,
        commission=config.backtest.commission,
        slippage=config.backtest.slippage
    )
    backtest_results = run_backtest_engine(price_data, signals_df['position'], backtest_config)
    
    # Step 5: Return results
    return {
        'config': config,
        'signals': signals_df,
        'fld': fld,
        'tdom': tdom_series,
        'tdoy': tdoy_series,
        'seasonal_score': seasonal_score,
        'equity': backtest_results['equity'],
        'returns': backtest_results['returns'],
        'trades': backtest_results['trades'],
        'stats': backtest_results['stats']
    }
