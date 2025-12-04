"""
Strategy Wrapper for Meridian v2.1.2

Provides consistent interface for all strategies.
"""

import pandas as pd
from typing import Any, Dict


class StrategyWrapper:
    """
    Wrapper providing uniform interface for any strategy.
    
    Allows strategies with different APIs to be called consistently.
    """
    
    def __init__(self, strategy: Any, name: str):
        """
        Initialize strategy wrapper.
        
        Args:
            strategy: Strategy instance
            name: Strategy identifier
        """
        self.strategy = strategy
        self.name = name
    
    def generate_signals(self, data_bundle: Dict[str, Any]) -> pd.Series:
        """
        Generate signals from strategy.
        
        Args:
            data_bundle: Dictionary with all required data (prices, fld, etc.)
        
        Returns:
            pd.Series: Trading signals (+1/0/-1)
        """
        # Call strategy's signal generation
        if hasattr(self.strategy, 'generate_signals'):
            result = self.strategy.generate_signals(**data_bundle)
            
            # Extract signal column if DataFrame returned
            if isinstance(result, pd.DataFrame) and 'signal' in result.columns:
                return result['signal']
            
            return result
        
        raise AttributeError(f"Strategy '{self.name}' has no generate_signals method")
    
    def get_name(self) -> str:
        """Get strategy name"""
        return self.name


