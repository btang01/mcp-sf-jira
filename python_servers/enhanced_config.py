#!/usr/bin/env python3
"""
Enhanced MCP Server Configuration
Strands SDK-inspired settings for production-grade capabilities
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class RetryConfig:
    """Retry policy configuration"""
    max_retries: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3

@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes
    max_size: int = 1000
    redis_url: Optional[str] = None

@dataclass
class MetricsConfig:
    """Metrics and observability configuration"""
    enabled: bool = True
    prometheus_port: int = 9090
    export_interval: int = 30

@dataclass
class ConnectionConfig:
    """Connection management configuration"""
    health_check_interval: int = 30
    connection_timeout: int = 10
    heartbeat_interval: int = 60

@dataclass
class EnhancedServerConfig:
    """Complete enhanced server configuration"""
    # Core settings
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    
    # Component configurations
    retry: RetryConfig = RetryConfig()
    circuit_breaker: CircuitBreakerConfig = CircuitBreakerConfig()
    cache: CacheConfig = CacheConfig()
    metrics: MetricsConfig = MetricsConfig()
    connection: ConnectionConfig = ConnectionConfig()
    
    # Feature flags
    enable_caching: bool = True
    enable_metrics: bool = True
    enable_circuit_breaker: bool = True
    enable_rate_limiting: bool = True
    enable_event_streaming: bool = True
    
    @classmethod
    def from_env(cls) -> 'EnhancedServerConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        config.host = os.getenv("MCP_HOST", config.host)
        config.port = int(os.getenv("MCP_PORT", config.port))
        config.debug = os.getenv("MCP_DEBUG", "false").lower() == "true"
        
        # Cache settings
        config.cache.enabled = os.getenv("MCP_CACHE_ENABLED", "true").lower() == "true"
        config.cache.ttl_seconds = int(os.getenv("MCP_CACHE_TTL", config.cache.ttl_seconds))
        config.cache.redis_url = os.getenv("REDIS_URL")
        
        # Retry settings
        config.retry.max_retries = int(os.getenv("MCP_MAX_RETRIES", config.retry.max_retries))
        config.retry.backoff_factor = float(os.getenv("MCP_BACKOFF_FACTOR", config.retry.backoff_factor))
        
        # Circuit breaker settings
        config.circuit_breaker.failure_threshold = int(os.getenv("MCP_CB_FAILURE_THRESHOLD", config.circuit_breaker.failure_threshold))
        config.circuit_breaker.recovery_timeout = int(os.getenv("MCP_CB_RECOVERY_TIMEOUT", config.circuit_breaker.recovery_timeout))
        
        # Feature flags
        config.enable_caching = os.getenv("MCP_ENABLE_CACHING", "true").lower() == "true"
        config.enable_metrics = os.getenv("MCP_ENABLE_METRICS", "true").lower() == "true"
        config.enable_circuit_breaker = os.getenv("MCP_ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
        
        return config

# Default configuration instance
DEFAULT_CONFIG = EnhancedServerConfig.from_env()