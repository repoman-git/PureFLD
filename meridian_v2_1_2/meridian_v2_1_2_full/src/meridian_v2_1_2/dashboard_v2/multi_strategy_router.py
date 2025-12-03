"""
Multi-Strategy Router for Dashboard v2

Manages registration and aggregation of multiple strategies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class StrategyState:
    """Standard strategy state object"""
    name: str
    pnl: float
    exposure: float
    risk_score: float
    signals: Dict[str, Any]
    shadow_state: Dict[str, Any]
    health: Dict[str, Any]
    allocation: float
    last_update: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = asdict(self)
        data['last_update'] = self.last_update.isoformat()
        return data


class MultiStrategyRouter:
    """
    Routes and aggregates multiple trading strategies.
    
    Provides unified interface for portfolio-level views.
    """
    
    def __init__(self):
        """Initialize router"""
        self.strategies: Dict[str, Any] = {}
        self._strategy_states: Dict[str, StrategyState] = {}
    
    def register_strategy(self, name: str, strategy_obj: Any):
        """
        Register a strategy.
        
        Args:
            name: Strategy identifier
            strategy_obj: Strategy object with required interface
        """
        if name in self.strategies:
            raise ValueError(f"Strategy '{name}' already registered")
        
        # Validate strategy object has required methods/attributes
        required = ['get_state', 'get_signals', 'get_pnl', 'get_exposure']
        missing = [attr for attr in required if not hasattr(strategy_obj, attr)]
        
        if missing:
            # Allow registration even if some methods missing
            # Will use defaults
            pass
        
        self.strategies[name] = strategy_obj
        
        # Also initialize empty state
        if name not in self._strategy_states:
            self._strategy_states[name] = None
    
    def unregister_strategy(self, name: str):
        """Remove strategy from router"""
        if name in self.strategies:
            del self.strategies[name]
        if name in self._strategy_states:
            del self._strategy_states[name]
    
    def list_strategies(self) -> List[str]:
        """Get list of registered strategy names"""
        return list(self.strategies.keys())
    
    def get_strategy(self, name: str) -> Optional[Any]:
        """Get strategy object by name"""
        return self.strategies.get(name)
    
    def update_strategy_state(self, name: str, state: StrategyState):
        """Update cached strategy state"""
        self._strategy_states[name] = state
    
    def get_strategy_state(self, name: str) -> Optional[StrategyState]:
        """Get strategy state"""
        if name in self._strategy_states:
            return self._strategy_states[name]
        
        # Try to fetch from strategy object
        strategy = self.get_strategy(name)
        if strategy and hasattr(strategy, 'get_state'):
            try:
                state_dict = strategy.get_state()
                return self._dict_to_strategy_state(name, state_dict)
            except Exception:
                pass
        
        return None
    
    def aggregate_portfolio_state(self) -> Dict[str, Any]:
        """
        Aggregate all strategies into portfolio-level metrics.
        
        Returns:
            Dictionary with portfolio totals and per-strategy breakdown
        """
        if not self.strategies:
            return {
                'total_pnl': 0.0,
                'total_exposure': 0.0,
                'total_risk': 0.0,
                'num_strategies': 0,
                'strategies': [],
                'timestamp': datetime.now().isoformat()
            }
        
        total_pnl = 0.0
        total_exposure = 0.0
        total_risk = 0.0
        strategies_data = []
        
        # Get unique strategy names from both sources
        all_names = set(list(self.strategies.keys()) + list(self._strategy_states.keys()))
        
        for name in all_names:
            state = self.get_strategy_state(name)
            
            if state:
                total_pnl += state.pnl
                total_exposure += state.exposure
                total_risk += state.risk_score
                
                strategies_data.append({
                    'name': name,
                    'pnl': state.pnl,
                    'exposure': state.exposure,
                    'risk_score': state.risk_score,
                    'allocation': state.allocation,
                    'health_status': state.health.get('status', 'unknown'),
                    'last_update': state.last_update.isoformat()
                })
        
        return {
            'total_pnl': total_pnl,
            'total_exposure': total_exposure,
            'total_risk': total_risk,
            'num_strategies': len(self.strategies),
            'strategies': strategies_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix between strategies.
        
        Returns:
            DataFrame with strategy correlations
        """
        if len(self.strategies) < 2:
            return pd.DataFrame()
        
        # Collect returns for each strategy
        returns_dict = {}
        
        for name in self.strategies:
            state = self.get_strategy_state(name)
            if state and 'returns' in state.signals:
                returns_dict[name] = state.signals['returns']
        
        if len(returns_dict) < 2:
            # Return empty correlation matrix
            names = list(self.strategies.keys())
            return pd.DataFrame(
                [[1.0 if i == j else 0.0 for j in range(len(names))] 
                 for i in range(len(names))],
                index=names,
                columns=names
            )
        
        # Calculate correlations
        returns_df = pd.DataFrame(returns_dict)
        return returns_df.corr()
    
    def _dict_to_strategy_state(self, name: str, state_dict: Dict[str, Any]) -> StrategyState:
        """Convert dictionary to StrategyState"""
        return StrategyState(
            name=name,
            pnl=state_dict.get('pnl', 0.0),
            exposure=state_dict.get('exposure', 0.0),
            risk_score=state_dict.get('risk_score', 0.0),
            signals=state_dict.get('signals', {}),
            shadow_state=state_dict.get('shadow_state', {}),
            health=state_dict.get('health', {}),
            allocation=state_dict.get('allocation', 0.0),
            last_update=state_dict.get('last_update', datetime.now())
        )

