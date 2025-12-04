"""
Combined PnL Component

Aggregated PnL visualization across strategies.
"""

from typing import Dict, List, Any


class CombinedPnL:
    """
    Combined PnL component.
    
    Returns JSON-compatible PnL structure for plotting.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get combined PnL data.
        
        Returns:
            Dictionary with combined curve and per-strategy breakdown
        """
        pnl_data = self.api.get_portfolio_pnl()
        
        # Build per-strategy PnL history (placeholder for now)
        per_strategy = {}
        for strat in pnl_data['strategies']:
            per_strategy[strat['name']] = {
                'current_pnl': strat['pnl'],
                'contribution_pct': strat['contribution_pct'],
                # Historical curve would come from state
                'history': []
            }
        
        return {
            'total_pnl': pnl_data['total_pnl'],
            'combined_curve': [],  # Would be populated from historical data
            'per_strategy': per_strategy,
            'timestamp': pnl_data['timestamp']
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get PnL summary statistics"""
        data = self.get_data()
        
        return {
            'total': data['total_pnl'],
            'num_strategies': len(data['per_strategy']),
            'top_contributor': self._get_top_contributor(data['per_strategy']),
            'worst_contributor': self._get_worst_contributor(data['per_strategy'])
        }
    
    def _get_top_contributor(self, strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy with highest PnL"""
        if not strategies:
            return {'name': None, 'pnl': 0.0}
        
        top = max(strategies.items(), key=lambda x: x[1]['current_pnl'])
        return {'name': top[0], 'pnl': top[1]['current_pnl']}
    
    def _get_worst_contributor(self, strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy with lowest PnL"""
        if not strategies:
            return {'name': None, 'pnl': 0.0}
        
        worst = min(strategies.items(), key=lambda x: x[1]['current_pnl'])
        return {'name': worst[0], 'pnl': worst[1]['current_pnl']}


