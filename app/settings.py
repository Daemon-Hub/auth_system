from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    SECRET_KEY: str
    
    # PostgreSQL 
    DATABASE_URL: str
    
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )
    
    # JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = [
        '127.0.0.1'
    ]
    
    
settings = Settings()
