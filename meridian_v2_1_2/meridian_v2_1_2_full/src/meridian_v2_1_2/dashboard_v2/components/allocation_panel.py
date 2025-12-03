"""
Allocation Panel Component

Interactive capital distribution management.
"""

from typing import Dict, List, Any


class AllocationPanel:
    """
    Capital allocation management component.
    
    Manages capital distribution across strategies.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get allocation data.
        
        Returns:
            Dictionary with allocation breakdown
        """
        return self.api.get_allocations()
    
    def validate_allocations(self, allocations: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate allocation changes.
        
        Args:
            allocations: Dictionary of strategy_name -> allocation
        
        Returns:
            Validation result
        """
        total = sum(allocations.values())
        
        if abs(total - 1.0) > 0.01:  # Allow 1% tolerance
            return {
                'valid': False,
                'error': f'Allocations must sum to 1.0 (got {total:.2f})'
            }
        
        for name, alloc in allocations.items():
            if alloc < 0:
                return {
                    'valid': False,
                    'error': f'Negative allocation for {name}: {alloc}'
                }
            if alloc > 1.0:
                return {
                    'valid': False,
                    'error': f'Allocation > 100% for {name}: {alloc}'
                }
        
        return {
            'valid': True,
            'allocations': allocations,
            'total': total
        }
    
    def suggest_equal_weight(self) -> Dict[str, float]:
        """Suggest equal-weight allocation"""
        strategies = self.api.get_strategies()['strategies']
        
        if not strategies:
            return {}
        
        weight = 1.0 / len(strategies)
        return {name: weight for name in strategies}
    
    def suggest_risk_parity(self) -> Dict[str, float]:
        """Suggest risk-parity allocation"""
        risk_data = self.api.get_portfolio_risk()
        
        if not risk_data['strategies']:
            return {}
        
        # Inverse risk weighting
        inv_risks = []
        for strat in risk_data['strategies']:
            risk = strat['risk_score']
            inv_risk = 1.0 / risk if risk > 0 else 1.0
            inv_risks.append((strat['name'], inv_risk))
        
        total_inv_risk = sum(r for _, r in inv_risks)
        
        return {
            name: inv_risk / total_inv_risk
            for name, inv_risk in inv_risks
        }

