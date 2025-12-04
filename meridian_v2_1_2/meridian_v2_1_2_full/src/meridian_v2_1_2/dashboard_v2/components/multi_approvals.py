"""
Multi-Approvals Component

Unified approval queue across all strategies.
"""

from typing import Dict, List, Any


class MultiApprovals:
    """
    Multi-strategy approval queue component.
    
    Aggregates pending approvals from all strategies.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get pending approvals.
        
        Returns:
            Dictionary with approval queue
        """
        return self.api.get_approvals()
    
    def get_by_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get approvals grouped by priority.
        
        Returns:
            Dictionary with high/medium/low priority groups
        """
        data = self.get_data()
        
        grouped = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for approval in data.get('approvals', []):
            priority = approval.get('priority', 'medium').lower()
            if priority in grouped:
                grouped[priority].append(approval)
        
        return grouped
    
    def get_by_strategy(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get approvals grouped by strategy.
        
        Returns:
            Dictionary with strategy-grouped approvals
        """
        data = self.get_data()
        
        grouped = {}
        
        for approval in data.get('approvals', []):
            strategy = approval.get('strategy', 'unknown')
            if strategy not in grouped:
                grouped[strategy] = []
            grouped[strategy].append(approval)
        
        return grouped


