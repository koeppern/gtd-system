"""
Application configuration using YAML config file
"""
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import yaml
from pydantic import BaseModel
from functools import lru_cache


class DatabaseConfig(BaseModel):
    """Database configuration"""
    supabase: Dict[str, str]
    postgres: Dict[str, Optional[str]]
    test: Dict[str, str]


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class CorsConfig(BaseModel):
    """CORS configuration"""
    origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]


class AppConfig(BaseModel):
    """Application configuration"""
    name: str
    version: str
    environment: str
    debug: bool


class ServerConfig(BaseModel):
    """Server configuration"""
    host: str
    port: int


class ApiConfig(BaseModel):
    """API configuration"""
    prefix: str
    docs_url: str
    redoc_url: str
    openapi_url: str


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str
    format: str


class PaginationConfig(BaseModel):
    """Pagination configuration"""
    default_limit: int
    max_limit: int


class GTDConfig(BaseModel):
    """GTD specific configuration"""
    default_user_id: str
    tasks: Dict[str, Any]
    projects: Dict[str, Any]
    weekly_review: Dict[str, Any]


class FeaturesConfig(BaseModel):
    """Feature flags configuration"""
    authentication_enabled: bool
    real_time_updates: bool
    email_notifications: bool
    export_import: bool


class Settings(BaseModel):
    """Main settings class that loads from YAML"""
    app: AppConfig
    server: ServerConfig
    database: DatabaseConfig
    security: SecurityConfig
    cors: CorsConfig
    logging: LoggingConfig
    api: ApiConfig
    pagination: PaginationConfig
    gtd: GTDConfig
    features: FeaturesConfig
    
    @classmethod
    def from_yaml(cls, config_path: Path) -> "Settings":
        """Load settings from YAML file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
    
    @property
    def database_url_asyncpg(self) -> str:
        """Get async PostgreSQL URL"""
        # First check if direct postgres URL is provided
        if self.database.postgres["url"]:
            return self.database.postgres["url"]
        
        # Otherwise construct from Supabase URL
        supabase_url = self.database.supabase["url"]
        service_key = self.database.supabase["service_role_key"]
        
        # Override with environment variables if present
        supabase_url = os.getenv("SUPABASE_URL", supabase_url)
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", service_key)
        
        if supabase_url and service_key:
            project_id = supabase_url.split("//")[1].split(".")[0]
            return f"postgresql+asyncpg://postgres:{service_key}@db.{project_id}.supabase.co:5432/postgres"
        
        raise ValueError("Database configuration not properly set")
    
    @property
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.app.environment == "testing" or os.getenv("PYTEST_CURRENT_TEST") is not None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    # Determine config file path
    config_file = os.getenv("CONFIG_FILE", "config/config.yaml")
    
    # Support both absolute and relative paths
    if not Path(config_file).is_absolute():
        # Look for config file relative to project root
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / config_file
    else:
        config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    return Settings.from_yaml(config_path)


# Create settings instance
settings = get_settings()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
TESTS_DIR = BASE_DIR / "tests"
CONFIG_DIR = BASE_DIR.parent / "config"