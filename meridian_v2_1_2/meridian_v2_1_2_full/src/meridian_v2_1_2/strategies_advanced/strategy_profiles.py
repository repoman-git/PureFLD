"""
Strategy Profiles (Scaffold)

Future: Deep strategy profiling and metadata extraction.

⚠️  STUB - Placeholder for future implementation
"""

from typing import Dict, Any


def describe_strategy(strategy_name: str) -> Dict[str, Any]:
    """
    Return comprehensive strategy description.
    
    Future implementation will include:
    - Trading rules in natural language
    - Entry/exit conditions
    - Risk parameters
    - Historical behavior patterns
    - Volatility regimes
    - Expected holding periods
    
    Args:
        strategy_name: Name of strategy
    
    Returns:
        Dictionary with strategy profile
    
    ⚠️  STUB - Returns placeholder data
    """
    return {
        'name': strategy_name,
        'description': f'Strategy profile for {strategy_name}',
        'rules': ['Placeholder rule 1', 'Placeholder rule 2'],
        'parameters': {},
        'risk_profile': 'medium',
        'best_regimes': ['trending', 'volatile'],
        'status': 'stub_implementation'
    }


def get_strategy_profile(strategy_obj: Any) -> Dict[str, Any]:
    """
    Extract detailed profile from strategy object.
    
    Future: Introspection of strategy logic, parameters, and behavior.
    
    Args:
        strategy_obj: Strategy instance
    
    Returns:
        Complete strategy profile
    
    ⚠️  STUB - Returns minimal data
    """
    return {
        'name': getattr(strategy_obj, 'name', 'Unknown'),
        'params': getattr(strategy_obj, 'params', {}),
        'status': 'stub_implementation'
    }


