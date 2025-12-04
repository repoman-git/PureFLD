"""
Event Bus for Meridian v2.1.2

Lightweight pub/sub system for streaming events.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Callable
from datetime import datetime


class EventType(str, Enum):
    """Event types"""
    MARKET_UPDATE = "market_update"
    POSITIONS_UPDATE = "positions_update"
    ORDERS_UPDATE = "orders_update"
    FILLS_UPDATE = "fills_update"
    ACCOUNT_UPDATE = "account_update"
    DRIFT_UPDATE = "drift_update"
    OVERSIGHT_UPDATE = "oversight_update"
    DASHBOARD_PUSH = "dashboard_push"
    STREAM_ERROR = "stream_error"


@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str


class EventBus:
    """
    Simple pub/sub event bus.
    
    Allows modules to react to streaming updates without tight coupling.
    """
    
    def __init__(self):
        """Initialize event bus"""
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Store in history
        self.event_history.append(event)
        
        # Keep history bounded
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        
        # Notify subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def get_recent_events(
        self,
        event_type: EventType = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get recent events.
        
        Args:
            event_type: Filter by event type
            limit: Max events to return
        
        Returns:
            List of events
        """
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self.event_history = []


