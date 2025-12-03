"""
Multi-Strategy API for Dashboard v2

JSON endpoints for multi-strategy portfolio data.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

from .multi_strategy_router import MultiStrategyRouter


class MultiStrategyAPI:
    """
    REST-like API for multi-strategy portfolio queries.
    
    All responses are JSON-serializable dictionaries.
    """
    
    def __init__(self, router: MultiStrategyRouter):
        """
        Initialize API.
        
        Args:
            router: MultiStrategyRouter instance
        """
        self.router = router
    
    def get_strategies(self) -> Dict[str, Any]:
        """
        GET /api/strategies
        
        Returns list of all registered strategies.
        """
        strategies = self.router.list_strategies()
        
        return {
            'strategies': strategies,
            'count': len(strategies),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_strategy_state(self, strategy_id: str) -> Dict[str, Any]:
        """
        GET /api/strategy/<id>/state
        
        Returns detailed state for single strategy.
        """
        state = self.router.get_strategy_state(strategy_id)
        
        if state is None:
            return {
                'error': f"Strategy '{strategy_id}' not found",
                'status': 404
            }
        
        return {
            'strategy': state.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_portfolio_overview(self) -> Dict[str, Any]:
        """
        GET /api/portfolio/overview
        
        Returns aggregated portfolio metrics.
        """
        return self.router.aggregate_portfolio_state()
    
    def get_portfolio_risk(self) -> Dict[str, Any]:
        """
        GET /api/portfolio/risk
        
        Returns risk breakdown across strategies.
        """
        portfolio = self.router.aggregate_portfolio_state()
        
        strategies_risk = []
        for strat in portfolio['strategies']:
            strategies_risk.append({
                'name': strat['name'],
                'risk_score': strat['risk_score'],
                'exposure': strat['exposure'],
                'risk_contribution': (strat['risk_score'] / portfolio['total_risk']
                                    if portfolio['total_risk'] > 0 else 0.0)
            })
        
        return {
            'total_risk': portfolio['total_risk'],
            'strategies': strategies_risk,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_portfolio_correlation(self) -> Dict[str, Any]:
        """
        GET /api/portfolio/correlation
        
        Returns correlation matrix between strategies.
        """
        corr_matrix = self.router.get_correlation_matrix()
        
        if corr_matrix.empty:
            return {
                'correlation_matrix': [],
                'strategies': [],
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'correlation_matrix': corr_matrix.values.tolist(),
            'strategies': corr_matrix.index.tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_portfolio_pnl(self) -> Dict[str, Any]:
        """
        GET /api/portfolio/pnl
        
        Returns PnL breakdown.
        """
        portfolio = self.router.aggregate_portfolio_state()
        
        strategies_pnl = []
        for strat in portfolio['strategies']:
            strategies_pnl.append({
                'name': strat['name'],
                'pnl': strat['pnl'],
                'contribution_pct': (strat['pnl'] / portfolio['total_pnl'] * 100
                                   if portfolio['total_pnl'] != 0 else 0.0)
            })
        
        return {
            'total_pnl': portfolio['total_pnl'],
            'strategies': strategies_pnl,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_approvals(self) -> Dict[str, Any]:
        """
        GET /api/approvals
        
        Returns pending approvals across all strategies.
        """
        pending = []
        
        for name in self.router.list_strategies():
            state = self.router.get_strategy_state(name)
            if state and 'pending_approvals' in state.signals:
                for approval in state.signals['pending_approvals']:
                    pending.append({
                        'strategy': name,
                        **approval
                    })
        
        return {
            'pending_count': len(pending),
            'approvals': pending,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_allocations(self) -> Dict[str, Any]:
        """
        GET /api/allocations
        
        Returns capital allocation across strategies.
        """
        portfolio = self.router.aggregate_portfolio_state()
        
        allocations = []
        for strat in portfolio['strategies']:
            allocations.append({
                'name': strat['name'],
                'allocation': strat['allocation'],
                'exposure': strat['exposure']
            })
        
        return {
            'total_allocation': sum(a['allocation'] for a in allocations),
            'allocations': allocations,
            'timestamp': datetime.now().isoformat()
        }
    
    def to_json(self, data: Dict[str, Any]) -> str:
        """Convert response to JSON string"""
        return json.dumps(data, indent=2, default=str)

