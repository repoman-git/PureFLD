"""
Strategy Router

Routes strategy names to implementations.
Provides strategy metadata for UI display.

⚠️  EDUCATIONAL ONLY - Paper trading simulation
"""

from typing import Dict, Any, List, Optional
from . import ETF_STRATEGIES


# Strategy metadata for UI display
STRATEGY_METADATA = {
    'FLD-ETF': {
        'name': 'FLD-ETF',
        'description': 'Future Line of Demarcation cycle analysis for ETFs',
        'asset_classes': ['ETF'],
        'best_for': ['GLD', 'SLV', 'TLT', 'SPY', 'QQQ'],
        'default_params': {
            'cycle': 20,
            'displacement': 10,
            'allow_short': False,
            'stop_loss': 0.02,
            'take_profit': 0.05
        },
        'rules': [
            'Long when price > FLD line',
            'Exit when price < FLD line',
            'FLD = displaced moving average',
            'Cycle-based timing'
        ]
    },
    'Momentum-ETF': {
        'name': 'Momentum-ETF',
        'description': 'Classic momentum strategy for ETFs',
        'asset_classes': ['ETF'],
        'best_for': ['SPY', 'QQQ', 'IWM', 'DIA'],
        'default_params': {
            'lookback': 20,
            'allow_short': False,
            'stop_loss': 0.03
        },
        'rules': [
            'Long on positive momentum',
            'Exit on momentum reversal',
            'Trend-following logic'
        ]
    },
    'Cycle-ETF': {
        'name': 'Cycle-ETF',
        'description': 'Seasonal cycle-based strategy for ETFs',
        'asset_classes': ['ETF'],
        'best_for': ['GLD', 'TLT', 'XLE', 'XLF'],
        'default_params': {
            'cycle_length': 30,
            'allow_short': False
        },
        'rules': [
            'Long in favorable cycle phase',
            'Exit in unfavorable phase',
            'Seasonal pattern recognition'
        ]
    },
    'Defensive-ETF': {
        'name': 'Defensive-ETF',
        'description': 'Conservative risk-managed ETF strategy',
        'asset_classes': ['ETF'],
        'best_for': ['TLT', 'GLD', 'IEF', 'SHY'],
        'default_params': {
            'volatility_threshold': 0.20,
            'allow_short': False
        },
        'rules': [
            'Long in low-volatility regimes',
            'Exit on volatility spikes',
            'Risk-first approach'
        ]
    }
}


def list_strategies() -> List[str]:
    """
    Return list of available strategy names.
    
    Returns:
        List of strategy names
    """
    return list(ETF_STRATEGIES.keys())


def load_strategy(strategy_name: str, params: Optional[Dict[str, Any]] = None):
    """
    Load and instantiate a strategy.
    
    Args:
        strategy_name: Name of strategy (e.g., 'FLD-ETF')
        params: Optional parameters (uses defaults if not provided)
    
    Returns:
        Instantiated strategy object
    
    Raises:
        ValueError: If strategy not found
    """
    if strategy_name not in ETF_STRATEGIES:
        raise ValueError(
            f"Strategy '{strategy_name}' not found. "
            f"Available: {list_strategies()}"
        )
    
    # Get strategy class
    strategy_class = ETF_STRATEGIES[strategy_name]
    
    # Use default params if not provided
    if params is None:
        params = get_strategy_metadata(strategy_name)['default_params']
    
    # Instantiate and return
    return strategy_class(params)


def get_strategy_metadata(strategy_name: str) -> Dict[str, Any]:
    """
    Get strategy metadata for UI display.
    
    Args:
        strategy_name: Name of strategy
    
    Returns:
        Dictionary with:
            - name: Strategy name
            - description: Human-readable description
            - asset_classes: Supported asset classes
            - best_for: Recommended symbols
            - default_params: Default parameters
            - rules: Trading rules as list of strings
    
    Raises:
        ValueError: If strategy not found
    """
    if strategy_name not in STRATEGY_METADATA:
        raise ValueError(f"Metadata not found for strategy: {strategy_name}")
    
    return STRATEGY_METADATA[strategy_name]


def get_all_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Get metadata for all strategies.
    
    Returns:
        Dictionary mapping strategy_name -> metadata
    """
    return STRATEGY_METADATA.copy()

