"""
Application configuration using YAML config file
"""
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import yaml
from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
        """Get async database URL"""
        # First check environment variable for direct database URL
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            return env_db_url
            
        # For testing, use test URL or postgres URL if available
        if self.is_testing and self.database.test.get("url"):
            return self.database.test["url"]
            
        # First check if direct postgres URL is provided
        if self.database.postgres.get("url"):
            return self.database.postgres["url"]
        
        # Otherwise construct from Supabase URL
        supabase_url = self.database.supabase.get("url", "")
        service_key = self.database.supabase.get("service_role_key", "")
        
        # Override with environment variables if present
        supabase_url = os.getenv("SUPABASE_URL", supabase_url)
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", service_key)
        
        if supabase_url and service_key:
            project_id = supabase_url.split("//")[1].split(".")[0]
            # Use pooler endpoint for better connectivity (IPv4 support)
            # Format: postgres.[project-ref]:[password]@[region].pooler.supabase.com:6543/postgres
            return f"postgresql+asyncpg://postgres.{project_id}:{service_key}@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
        
        # No database URL available
        raise ValueError("Database configuration incomplete: Missing Supabase URL or service role key")
    
    @property
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.app.environment == "testing" or os.getenv("PYTEST_CURRENT_TEST") is not None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    # Determine config file path - use relative paths only
    config_file = os.getenv("CONFIG_FILE", "config.yaml")
    
    # Start from this file's directory (app/)
    current_path = Path(__file__).parent
    config_path = None
    
    # Try common relative paths from app directory
    search_paths = [
        # From app/ directory
        current_path.parent.parent / "config" / config_file,  # ../../config/
        current_path.parent / "config" / config_file,  # ../config/
        current_path / "config" / config_file,  # ./config/
        
        # From backend/ directory (parent of app/)
        current_path.parent / config_file,  # ../
        
        # From src/ directory 
        current_path.parent.parent / config_file,  # ../../
        
        # From project root
        current_path.parent.parent.parent / "config" / config_file,  # ../../../config/
    ]
    
    # Also try relative to current working directory
    cwd = Path.cwd()
    search_paths.extend([
        cwd / "config" / config_file,
        cwd / config_file,
        cwd / ".." / "config" / config_file,
        cwd / ".." / ".." / "config" / config_file,
    ])
    
    # Find the first existing path
    for path in search_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        searched_paths = "\n".join(str(p) for p in search_paths)
        raise FileNotFoundError(f"Configuration file '{config_file}' not found. Searched paths:\n{searched_paths}")
    
    return Settings.from_yaml(config_path)


# Project paths (using relative paths)
BASE_DIR = Path(__file__).parent.parent  # Don't resolve immediately
APP_DIR = BASE_DIR / "app"
TESTS_DIR = BASE_DIR / "tests" 
CONFIG_DIR = BASE_DIR.parent / "config"