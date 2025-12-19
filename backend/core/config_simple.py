"""Configuration management for the Ariadne backend."""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


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
