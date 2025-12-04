"""
Rate Limiting for External APIs

Exponential backoff and retry logic.
"""

import time
from typing import Callable, Any
from collections import deque
from datetime import datetime, timedelta


class RateLimiter:
    """
    Rate limiter with exponential backoff.
    
    Tracks API calls and enforces limits.
    """
    
    def __init__(
        self,
        calls_per_second: float = 5.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum calls per second
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay in seconds
        """
        self.calls_per_second = calls_per_second
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Track recent calls
        self.call_times = deque()
        self.window = 1.0  # 1 second window
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old calls outside window
        while self.call_times and self.call_times[0] < now - self.window:
            self.call_times.popleft()
        
        # Check if at limit
        if len(self.call_times) >= self.calls_per_second:
            # Calculate wait time
            oldest_call = self.call_times[0]
            wait_time = self.window - (now - oldest_call)
            
            if wait_time > 0:
                time.sleep(wait_time)
        
        # Record this call
        self.call_times.append(time.time())
    
    def call_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call function with rate limiting and retry logic.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        
        Raises:
            Exception if all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Wait if needed
                self.wait_if_needed()
                
                # Call function
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
        
        # All retries exhausted
        raise last_exception


def exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Any:
    """
    Simple exponential backoff wrapper.
    
    Args:
        func: Function to call
        max_retries: Maximum attempts
        initial_delay: Initial delay in seconds
    
    Returns:
        Function result
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = initial_delay * (2 ** attempt)
            time.sleep(delay)


