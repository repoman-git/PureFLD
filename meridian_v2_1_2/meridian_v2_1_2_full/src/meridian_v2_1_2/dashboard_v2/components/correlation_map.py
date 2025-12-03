"""
Correlation Map Component

Strategy correlation visualization.
"""

from typing import Dict, List, Any


class CorrelationMap:
    """
    Correlation matrix component.
    
    Returns 2D correlation matrix for visualization.
    """
    
    def __init__(self, api):
        """Initialize component"""
        self.api = api
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get correlation matrix data.
        
        Returns:
            Dictionary with correlation matrix and labels
        """
        return self.api.get_portfolio_correlation()
    
    def get_formatted_matrix(self) -> List[List[float]]:
        """Get correlation matrix as 2D list"""
        data = self.get_data()
        return data.get('correlation_matrix', [[]])
    
    def get_labels(self) -> List[str]:
        """Get strategy labels"""
        data = self.get_data()
        return data.get('strategies', [])

