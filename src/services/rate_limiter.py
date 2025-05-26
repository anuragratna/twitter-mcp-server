"""
Rate Limiter Service
Handles request rate limiting
"""

import time
from typing import Dict, List

class RateLimiter:
    def __init__(self, requests_per_window: int = 100, window_seconds: int = 3600):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is within rate limits."""
        now = time.time()
        
        # Clean up old entries
        self.request_counts.update({
            ip: [timestamp for timestamp in timestamps 
                if now - timestamp < self.window_seconds]
            for ip, timestamps in self.request_counts.items()
        })
        
        # Check current IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        if len(self.request_counts[client_ip]) >= self.requests_per_window:
            return False
        
        self.request_counts[client_ip].append(now)
        return True 