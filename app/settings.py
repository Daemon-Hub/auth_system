from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PostgreSQL 
    DATABASE_URL: str
    
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )
    
    # JWT
    SECRET_KEY: str = 'hoR1PIo6Gepq9-YTluIF6siSKdnmdjES0vKonPNq_Wk'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        '127.0.0.1'
    ]
    
    
settings = Settings()
