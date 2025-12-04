"""
Strategy Comparison Component

Matrix comparing signals, exposure, risk, and agreement.
"""

from typing import Dict, List, Any


class StrategyComparison:
    """
    Strategy comparison matrix component.
    
    Compares strategies across multiple dimensions.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get comparison matrix data.
        
        Returns:
            Dictionary with comparison metrics
        """
        strategies_list = self.api.get_strategies()
        
        if len(strategies_list['strategies']) < 2:
            return {
                'strategies': [],
                'comparison_matrix': [],
                'message': 'Need at least 2 strategies for comparison'
            }
        
        comparison_data = []
        
        for strategy_name in strategies_list['strategies']:
            state = self.api.get_strategy_state(strategy_name)
            
            if 'error' in state:
                continue
            
            strategy_data = state['strategy']
            
            comparison_data.append({
                'name': strategy_name,
                'signal': strategy_data['signals'].get('current_signal', 0),
                'exposure': strategy_data['exposure'],
                'risk': strategy_data['risk_score'],
                'pnl': strategy_data['pnl']
            })
        
        # Calculate agreement metrics
        signals = [s['signal'] for s in comparison_data]
        agreement_pct = self._calculate_agreement(signals)
        
        return {
            'strategies': comparison_data,
            'agreement_pct': agreement_pct,
            'num_long': sum(1 for s in signals if s > 0),
            'num_short': sum(1 for s in signals if s < 0),
            'num_flat': sum(1 for s in signals if s == 0)
        }
    
    def _calculate_agreement(self, signals: List[float]) -> float:
        """Calculate percentage agreement"""
        if not signals:
            return 0.0
        
        # Simple majority agreement
        positive = sum(1 for s in signals if s > 0)
        negative = sum(1 for s in signals if s < 0)
        
        majority = max(positive, negative, len(signals) - positive - negative)
        
        return (majority / len(signals)) * 100 if signals else 0.0


