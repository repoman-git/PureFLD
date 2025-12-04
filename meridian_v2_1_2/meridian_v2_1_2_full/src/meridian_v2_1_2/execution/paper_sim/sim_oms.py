"""
Simulated OMS for Meridian v2.1.2

Order Management System logging.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class SimulatedOMS:
    """
    Simulated Order Management System.
    
    Logs all orders, fills, and positions.
    """
    
    def __init__(self, log_path: str = "logs/paper_sim/"):
        """
        Initialize OMS.
        
        Args:
            log_path: Path to log directory
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
    
    def write_orders(self, orders: List, date_str: str = None) -> str:
        """
        Write orders log.
        
        Args:
            orders: List of orders
            date_str: Date string (YYYYMMDD)
        
        Returns:
            str: Path to log file
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')
        
        log_file = self.log_path / f"{date_str}_orders.json"
        
        orders_data = [
            order.to_dict() if hasattr(order, 'to_dict') else order
            for order in orders
        ]
        
        with open(log_file, 'w') as f:
            json.dump(orders_data, f, indent=2)
        
        return str(log_file)
    
    def write_fills(self, fills: List[dict], date_str: str = None) -> str:
        """
        Write fills log.
        
        Args:
            fills: List of fills
            date_str: Date string
        
        Returns:
            str: Path to log file
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')
        
        log_file = self.log_path / f"{date_str}_fills.json"
        
        with open(log_file, 'w') as f:
            json.dump(fills, f, indent=2)
        
        return str(log_file)
    
    def write_positions(self, portfolio_dict: Dict, date_str: str = None) -> str:
        """
        Write positions log.
        
        Args:
            portfolio_dict: Portfolio state dictionary
            date_str: Date string
        
        Returns:
            str: Path to log file
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')
        
        log_file = self.log_path / f"{date_str}_positions.json"
        
        with open(log_file, 'w') as f:
            json.dump(portfolio_dict, f, indent=2)
        
        return str(log_file)
    
    def write_nav(self, nav_data: Dict, date_str: str = None) -> str:
        """
        Write NAV log.
        
        Args:
            nav_data: NAV data
            date_str: Date string
        
        Returns:
            str: Path to log file
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')
        
        log_file = self.log_path / f"{date_str}_nav.json"
        
        with open(log_file, 'w') as f:
            json.dump(nav_data, f, indent=2)
        
        return str(log_file)


def write_oms_logs(
    broker,
    log_path: str = "logs/paper_sim/",
    date_str: str = None
) -> Dict[str, str]:
    """
    Write all OMS logs for current state.
    
    Args:
        broker: Simulated broker
        log_path: Log directory
        date_str: Date string
    
    Returns:
        Dict of log file paths
    """
    oms = SimulatedOMS(log_path)
    
    # Get data
    orders = list(broker.orders.values())
    fills = broker.get_fills()
    portfolio_dict = broker.get_positions()
    
    nav_data = {
        'date': date_str or datetime.now().strftime('%Y%m%d'),
        'equity': portfolio_dict['equity'],
        'cash': portfolio_dict['cash'],
        'realized_pl': portfolio_dict['realized_pl'],
        'unrealized_pl': portfolio_dict['unrealized_pl']
    }
    
    # Write logs
    return {
        'orders': oms.write_orders(orders, date_str),
        'fills': oms.write_fills(fills, date_str),
        'positions': oms.write_positions(portfolio_dict, date_str),
        'nav': oms.write_nav(nav_data, date_str)
    }


