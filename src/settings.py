from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings:
    # PostgreSQL 
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # JWT
    SECRET_KEY: str = 'hoR1PIo6Gepq9-YTluIF6siSKdnmdjES0vKonPNq_Wk'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    model_config = SettingsConfigDict(
        env_file='../.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
settings = Settings()
