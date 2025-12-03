"""
Strategy Registry for Meridian v2.1.2

Register and manage multiple trading strategies.
"""

from typing import Dict, Any, Callable


class StrategyRegistry:
    """
    Registry for managing multiple trading strategies.
    
    Provides uniform interface for strategy registration, retrieval, and execution.
    """
    
    def __init__(self):
        self.strategies: Dict[str, Any] = {}
        self.enabled: Dict[str, bool] = {}
    
    def register(self, name: str, strategy_class: Any) -> None:
        """
        Register a strategy.
        
        Args:
            name: Strategy identifier
            strategy_class: Strategy class or instance
        """
        self.strategies[name] = strategy_class
        self.enabled[name] = True
    
    def get(self, name: str) -> Any:
        """
        Get registered strategy.
        
        Args:
            name: Strategy identifier
        
        Returns:
            Strategy class or instance
            
        Raises:
            KeyError: If strategy not registered
        """
        if name not in self.strategies:
            raise KeyError(f"Strategy '{name}' not registered")
        
        return self.strategies[name]
    
    def enable(self, name: str) -> None:
        """Enable a strategy"""
        if name in self.strategies:
            self.enabled[name] = True
    
    def disable(self, name: str) -> None:
        """Disable a strategy"""
        if name in self.strategies:
            self.enabled[name] = False
    
    def is_enabled(self, name: str) -> bool:
        """Check if strategy is enabled"""
        return self.enabled.get(name, False)
    
    def list_strategies(self) -> list:
        """List all registered strategies"""
        return list(self.strategies.keys())
    
    def list_enabled(self) -> list:
        """List enabled strategies"""
        return [name for name, enabled in self.enabled.items() if enabled]

