"""
Stream Engine for Meridian v2.1.2

Main streaming coordinator.
"""

import time
import threading
from typing import Optional
from datetime import datetime

from .streamer_config import StreamerConfig
from .event_bus import EventBus, Event, EventType
from .state_cache import StateCache
from .openbb_streamer import OpenBBStreamer
from .alpaca_streamer import AlpacaStreamer
from .stream_safety import StreamSafety


class StreamEngine:
    """
    Main streaming engine.
    
    Coordinates market data and broker state polling.
    Does NOT trigger trades - monitoring only.
    """
    
    def __init__(
        self,
        config: StreamerConfig,
        openbb_adapter=None,
        alpaca_adapter=None
    ):
        """
        Initialize stream engine.
        
        Args:
            config: StreamerConfig instance
            openbb_adapter: Optional OpenBBAdapter
            alpaca_adapter: Optional AlpacaAdapter
        """
        self.config = config
        
        # Core components
        self.event_bus = EventBus()
        self.cache = StateCache(max_size=config.max_cache_size)
        self.safety = StreamSafety(config)
        
        # Streamers
        self.openbb_streamer = OpenBBStreamer(config, openbb_adapter)
        self.alpaca_streamer = AlpacaStreamer(config, alpaca_adapter)
        
        # Threading
        self.running = False
        self.openbb_thread: Optional[threading.Thread] = None
        self.alpaca_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start streaming"""
        if not self.config.enabled:
            print("Streaming is disabled")
            return
        
        if self.running:
            print("Streaming already running")
            return
        
        self.running = True
        
        # Start OpenBB streaming
        if self.config.openbb_enabled:
            self.openbb_thread = threading.Thread(target=self._openbb_loop, daemon=True)
            self.openbb_thread.start()
        
        # Start Alpaca streaming
        if self.config.alpaca_enabled:
            self.alpaca_thread = threading.Thread(target=self._alpaca_loop, daemon=True)
            self.alpaca_thread.start()
        
        print("Streaming started")
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        print("Streaming stopped")
    
    def _openbb_loop(self):
        """OpenBB polling loop"""
        while self.running:
            if not self.safety.is_paused():
                try:
                    prices = self.openbb_streamer.poll_prices()
                    
                    # Update cache
                    for price_data in prices:
                        symbol = price_data['symbol']
                        self.cache.update_price(symbol, price_data)
                    
                    # Publish event
                    event = Event(
                        event_type=EventType.MARKET_UPDATE,
                        timestamp=datetime.now(),
                        data={'prices': prices},
                        source='openbb'
                    )
                    self.event_bus.publish(event)
                    
                    self.safety.check_openbb_health(True)
                
                except Exception as e:
                    print(f"OpenBB streaming error: {e}")
                    self.safety.check_openbb_health(False)
            
            time.sleep(self.config.openbb_interval_sec)
    
    def _alpaca_loop(self):
        """Alpaca polling loop"""
        while self.running:
            if not self.safety.is_paused():
                try:
                    broker_state = self.alpaca_streamer.poll_broker_state()
                    
                    # Update cache
                    if 'positions' in broker_state:
                        positions_dict = {
                            p['symbol']: p
                            for p in broker_state['positions']
                        }
                        self.cache.update_positions(positions_dict)
                    
                    if 'orders' in broker_state:
                        orders_dict = {
                            str(i): o
                            for i, o in enumerate(broker_state['orders'])
                        }
                        self.cache.update_orders(orders_dict)
                    
                    if 'account' in broker_state:
                        self.cache.update_account(broker_state['account'])
                    
                    # Publish events
                    if 'positions' in broker_state:
                        event = Event(
                            event_type=EventType.POSITIONS_UPDATE,
                            timestamp=datetime.now(),
                            data={'positions': broker_state['positions']},
                            source='alpaca'
                        )
                        self.event_bus.publish(event)
                    
                    self.safety.check_alpaca_health(True)
                
                except Exception as e:
                    print(f"Alpaca streaming error: {e}")
                    self.safety.check_alpaca_health(False)
            
            time.sleep(self.config.alpaca_interval_sec)
    
    def get_status(self) -> dict:
        """
        Get streaming status.
        
        Returns:
            Status dict
        """
        return {
            'running': self.running,
            'enabled': self.config.enabled,
            'safety': self.safety.get_status(),
            'openbb': {
                'enabled': self.config.openbb_enabled,
                'interval': self.config.openbb_interval_sec
            },
            'alpaca': {
                'enabled': self.config.alpaca_enabled,
                'interval': self.config.alpaca_interval_sec
            }
        }

