"""Configuration management for the Ariadne backend."""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = Field(..., description="Database connection URL")
    echo: bool = Field(False, description="Enable SQL query logging")
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(20, description="Maximum overflow connections")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('Database URL must be PostgreSQL')
        return v


class Neo4jConfig(BaseModel):
    """Neo4j configuration."""
    uri: str = Field(..., description="Neo4j connection URI")
    username: str = Field(..., description="Neo4j username")
    password: str = Field(..., description="Neo4j password")
    database: str = Field("neo4j", description="Neo4j database name")
    max_connection_lifetime: int = Field(300, description="Max connection lifetime (seconds)")
    max_connection_pool_size: int = Field(50, description="Max connection pool size")
    
    @property
    def connection_string(self) -> str:
        """Get connection string for Neo4j driver."""
        return f"bolt://{self.uri}:7687"


class RedisConfig(BaseModel):
    """Redis configuration."""
    url: str = Field(..., description="Redis connection URL")
    max_connections: int = Field(20, description="Maximum Redis connections")
    retry_on_timeout: bool = Field(True, description="Retry on timeout")
    socket_timeout: int = Field(5, description="Socket timeout (seconds)")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Redis URL must start with redis:// or rediss://')
        return v


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field("openai", description="LLM provider (openai, anthropic)")
    model: str = Field("gpt-4o", description="Default model name")
    api_key: str = Field(..., description="API key")
    base_url: Optional[str] = Field(None, description="Custom base URL")
    max_tokens: int = Field(4000, description="Maximum tokens per request")
    temperature: float = Field(0.7, description="Model temperature")
    timeout: int = Field(60, description="Request timeout (seconds)")
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed_providers = ['openai', 'anthropic']
        if v not in allowed_providers:
            raise ValueError(f'Provider must be one of: {allowed_providers}')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class SecurityConfig(BaseModel):
    """Security configuration."""
    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field("RS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration (minutes)")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration (days)")
    bcrypt_rounds: int = Field(12, description="BCrypt rounds")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters')
        return v


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    anonymous_requests_per_hour: int = Field(10, description="Anonymous requests per hour")
    anonymous_requests_per_day: int = Field(50, description="Anonymous requests per day")
    authenticated_requests_per_hour: int = Field(100, description="Authenticated requests per hour")
    authenticated_requests_per_day: int = Field(1000, description="Authenticated requests per day")
    burst_limit: int = Field(5, description="Burst request limit")


class ContextConfig(BaseModel):
    """Context management configuration."""
    max_tokens_per_query: int = Field(50000, description="Maximum tokens per query context")
    diversity_weight: float = Field(0.3, description="Diversity weight in ranking")
    recency_weight: float = Field(0.2, description="Recency weight in ranking")
    preference_weight: float = Field(0.3, description="User preference weight in ranking")
    trust_weight: float = Field(0.2, description="Source trust weight in ranking")
    chunk_size: int = Field(1000, description="Text chunk size for embeddings")
    chunk_overlap: int = Field(200, description="Chunk overlap for better context")
    
    @validator('*_weight')
    def validate_weights(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Weights must be between 0.0 and 1.0')
        return v


class TemporalConfig(BaseModel):
    """Temporal workflow configuration."""
    address: str = Field("localhost:7233", description="Temporal server address")
    namespace: str = Field("default", description="Temporal namespace")
    task_queue: str = Field("ariadne-queries", description="Temporal task queue")
    retry_max_attempts: int = Field(3, description="Maximum retry attempts")
    retry_initial_interval: int = Field(1, description="Initial retry interval (seconds)")
    retry_max_interval: int = Field(60, description="Maximum retry interval (seconds)")
    
    @validator('address')
    def validate_address(cls, v):
        if ':' not in v:
            raise ValueError('Address must include port (e.g., localhost:7233)')
        return v


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""
    enable_tracing: bool = Field(True, description="Enable OpenTelemetry tracing")
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    enable_logging: bool = Field(True, description="Enable structured logging")
    log_level: str = Field("INFO", description="Log level")
    metrics_endpoint: str = Field("/metrics", description="Prometheus metrics endpoint")
    tracing_endpoint: str = Field("/v1/traces", description="OTLP tracing endpoint")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    enable_anonymous_queries: bool = Field(True, description="Enable anonymous queries")
    enable_muse_service: bool = Field(True, description="Enable proactive discovery service")
    enable_learning_models: bool = Field(True, description="Enable learning models")
    enable_tapestry_editing: bool = Field(True, description="Enable tapestry editing")
    enable_collaboration: bool = Field(True, description="Enable collaborative features")
    enable_marketplace: bool = Field(False, description="Enable plugin marketplace")
    enable_export_engine: bool = Field(True, description="Enable export engine")
    
    # Model-specific feature flags
    enable_gpt4: bool = Field(True, description="Enable GPT-4 models")
    enable_claude: bool = Field(True, description="Enable Claude models")
    enable_local_models: bool = Field(False, description="Enable local model inference")


class AriadneSettings(BaseSettings):
    """Main application settings."""
    
    # Application
    app_name: str = Field("Ariadne", description="Application name")
    app_version: str = Field("0.1.0", description="Application version")
    debug: bool = Field(False, description="Debug mode")
    environment: str = Field("development", description="Environment")
    
    # Server
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    workers: int = Field(1, description="Number of workers")
    reload: bool = Field(False, description="Auto-reload on code changes")
    
    # CORS
    allowed_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    allowed_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        ["*"],
        description="Allowed HTTP headers"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Global settings instance
_settings = None


def get_settings() -> AriadneSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = AriadneSettings()
    return _settings


def reload_settings() -> AriadneSettings:
    """Reload settings from environment (useful for testing)."""
    global _settings
    _settings = None
    return get_settings()
