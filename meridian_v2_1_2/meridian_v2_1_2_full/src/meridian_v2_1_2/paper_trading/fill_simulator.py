"""
Fill Simulator

Simulates order execution with realistic fill logic and slippage.

⚠️  SIMULATED FILLS ONLY - NO REAL TRADING
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimulatedFill:
    """Result of simulated order fill"""
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    fill_price: float
    slippage: float
    timestamp: str
    audit_status: str  # 'APPROVED', 'WARNING', 'BLOCKED'
    success: bool


class FillSimulator:
    """
    Simulates order fills with slippage model.
    
    Integrates with Trading Audit Engine.
    
    ⚠️  PAPER TRADING ONLY - NO REAL EXECUTION
    """
    
    def __init__(self, slippage_bps: float = 5.0):
        """
        Initialize fill simulator.
        
        Args:
            slippage_bps: Slippage in basis points (default: 5 = 0.05%)
        """
        self.slippage_bps = slippage_bps
    
    def simulate_market_order(
        self,
        symbol: str,
        quantity: float,
        last_price: float,
        side: str,
        audit_result: Optional[Dict[str, Any]] = None
    ) -> SimulatedFill:
        """
        Simulate market order fill.
        
        Args:
            symbol: Asset symbol
            quantity: Order quantity
            last_price: Last traded price
            side: 'BUY' or 'SELL'
            audit_result: Trading audit result (optional)
        
        Returns:
            SimulatedFill with fill details
        """
        # Check audit
        if audit_result:
            if audit_result.get('final_status') == 'BLOCKED':
                return SimulatedFill(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    fill_price=0.0,
                    slippage=0.0,
                    timestamp=datetime.now().isoformat(),
                    audit_status='BLOCKED',
                    success=False
                )
        
        # Calculate slippage
        slippage_pct = self.slippage_bps / 10000.0
        
        if side == 'BUY':
            # Pay the ask (worse for buyer)
            fill_price = last_price * (1 + slippage_pct)
        else:  # SELL
            # Hit the bid (worse for seller)
            fill_price = last_price * (1 - slippage_pct)
        
        slippage = abs(fill_price - last_price)
        
        return SimulatedFill(
            symbol=symbol,
            side=side,
            quantity=quantity,
            fill_price=fill_price,
            slippage=slippage,
            timestamp=datetime.now().isoformat(),
            audit_status=audit_result.get('final_status', 'APPROVED') if audit_result else 'APPROVED',
            success=True
        )
    
    def simulate_limit_order(
        self,
        symbol: str,
        quantity: float,
        limit_price: float,
        last_price: float,
        side: str,
        audit_result: Optional[Dict[str, Any]] = None
    ) -> SimulatedFill:
        """
        Simulate limit order fill.
        
        Args:
            symbol: Asset symbol
            quantity: Order quantity
            limit_price: Limit price
            last_price: Current market price
            side: 'BUY' or 'SELL'
            audit_result: Trading audit result
        
        Returns:
            SimulatedFill (may not fill if price doesn't cross limit)
        """
        # Check audit
        if audit_result:
            if audit_result.get('final_status') == 'BLOCKED':
                return SimulatedFill(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    fill_price=0.0,
                    slippage=0.0,
                    timestamp=datetime.now().isoformat(),
                    audit_status='BLOCKED',
                    success=False
                )
        
        # Check if limit would fill
        filled = False
        
        if side == 'BUY':
            # Buy limit fills if market <= limit
            if last_price <= limit_price:
                filled = True
                fill_price = min(last_price, limit_price)
        else:  # SELL
            # Sell limit fills if market >= limit
            if last_price >= limit_price:
                filled = True
                fill_price = max(last_price, limit_price)
        
        if not filled:
            return SimulatedFill(
                symbol=symbol,
                side=side,
                quantity=quantity,
                fill_price=0.0,
                slippage=0.0,
                timestamp=datetime.now().isoformat(),
                audit_status='PENDING',
                success=False
            )
        
        return SimulatedFill(
            symbol=symbol,
            side=side,
            quantity=quantity,
            fill_price=fill_price,
            slippage=abs(fill_price - last_price),
            timestamp=datetime.now().isoformat(),
            audit_status=audit_result.get('final_status', 'APPROVED') if audit_result else 'APPROVED',
            success=True
        )

