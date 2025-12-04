"""
Strategy Cards Component

Grid of mini panels for each strategy.
"""

from typing import Dict, List, Any


class StrategyCards:
    """
    Strategy card grid component.
    
    Displays health status for each strategy in card format.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> List[Dict[str, Any]]:
        """
        Get strategy card data.
        
        Returns:
            List of strategy card objects
        """
        strategies_list = self.api.get_strategies()
        cards = []
        
        for strategy_name in strategies_list['strategies']:
            state = self.api.get_strategy_state(strategy_name)
            
            if 'error' in state:
                continue
            
            strategy_data = state['strategy']
            
            # Build card
            card = {
                'name': strategy_data['name'],
                'pnl': strategy_data['pnl'],
                'exposure': strategy_data['exposure'],
                'risk_score': strategy_data['risk_score'],
                'allocation': strategy_data['allocation'],
                'health_status': strategy_data['health'].get('status', 'unknown'),
                'last_update': strategy_data['last_update'],
                'status_emoji': self._get_status_emoji(strategy_data['health'].get('status', 'unknown'))
            }
            
            cards.append(card)
        
        return cards
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for health status"""
        return {
            'ok': '✅',
            'healthy': '✅',
            'warning': '⚠️',
            'error': '❌',
            'unknown': '❓'
        }.get(status.lower(), '❓')


