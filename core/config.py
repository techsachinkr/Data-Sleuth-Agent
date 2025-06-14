import os,sys
sys.path.append(os.getcwd())
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Intelligence Gathering Service"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Model Configuration
    QUERY_ANALYSIS_MODEL: str = "claude-3-5-sonnet"
    PLANNING_MODEL: str = "gpt-4"
    RETRIEVAL_MODEL: str = "claude-3-5-sonnet"
    PIVOT_MODEL: str = "gpt-4-turbo"
    SYNTHESIS_MODEL: str = "claude-3-opus"
    
    # Memory Configuration
    MAX_CONTEXT_TOKENS: int = 100000
    MAX_EVIDENCE_ITEMS: int = 1000
    
    # Database Configuration (if needed)
    DATABASE_URL: Optional[str] = None
    
    # Redis Configuration (for caching)
    REDIS_URL: Optional[str] = None
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()