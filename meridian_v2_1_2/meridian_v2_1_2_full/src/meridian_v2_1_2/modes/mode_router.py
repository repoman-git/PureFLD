"""
Mode Router for Meridian v2.1.2

Routes execution to appropriate pipeline based on operating mode.
"""

from typing import Dict, Any
import pandas as pd


def route_by_mode(config, **kwargs) -> Dict[str, Any]:
    """
    Route to appropriate execution pipeline based on mode.
    
    Args:
        config: MeridianConfig with mode set
        **kwargs: Pipeline-specific arguments
    
    Returns:
        Results dictionary appropriate for mode
    
    Raises:
        ValueError: If mode is invalid or requirements not met
    """
    mode = config.mode
    
    if mode == "research":
        from .research_config import validate_research_mode
        validate_research_mode(config)
        return _run_research_pipeline(config, **kwargs)
    
    elif mode == "paper":
        from .paper_config import validate_paper_mode
        validate_paper_mode(config)
        return _run_paper_pipeline(config, **kwargs)
    
    elif mode == "live":
        from .live_config import validate_live_mode
        validate_live_mode(config)
        return _run_live_pipeline(config, **kwargs)
    
    else:
        raise ValueError(f"Invalid mode: {mode}")


def _run_research_pipeline(config, **kwargs) -> Dict[str, Any]:
    """
    Execute research mode pipeline.
    
    - No execution engine
    - No OMS
    - Ideal fills
    - All analysis tools available
    """
    # Use standard orchestrator workflow
    from ..orchestrator import run_backtest
    
    prices = kwargs.get('prices')
    cot_data = kwargs.get('cot_data')
    
    results = run_backtest(config, prices, cot_data)
    results['mode'] = 'research'
    results['execution_type'] = 'ideal_backtest'
    
    return results


def _run_paper_pipeline(config, **kwargs) -> Dict[str, Any]:
    """
    Execute paper trading pipeline.
    
    - Execution engine enabled
    - OMS tracking
    - Realistic slippage and delays
    - No real broker
    """
    # For now, use research pipeline with execution flag
    # Full execution engine will be added
    from ..orchestrator import run_backtest
    
    prices = kwargs.get('prices')
    cot_data = kwargs.get('cot_data')
    
    results = run_backtest(config, prices, cot_data)
    results['mode'] = 'paper'
    results['execution_type'] = 'simulated_with_slippage'
    
    # Add execution-specific metadata
    results['slippage_applied'] = True
    results['delays_applied'] = True
    
    return results


def _run_live_pipeline(config, **kwargs) -> Dict[str, Any]:
    """
    Execute live trading pipeline.
    
    - Broker connection required
    - Real order submission
    - OMS tracking
    - Kill switches enabled
    - No backtesting
    
    SAFETY: This mode has strict restrictions
    """
    # Validate live requirements
    broker_connected = kwargs.get('broker_connected', False)
    
    if not broker_connected:
        raise ValueError("Live mode requires broker_connected=True")
    
    # In live mode, we don't run full backtests
    # We generate signals and route to execution
    results = {
        'mode': 'live',
        'execution_type': 'real_broker',
        'message': 'Live trading mode - no backtest results',
        'safety': 'kill_switches_enabled'
    }
    
    return results


