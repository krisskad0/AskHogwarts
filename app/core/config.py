from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AskHogwarts"
    
    # Security
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "hogwarts-index"
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Character Settings
    DEFAULT_CHARACTERS: list[str] = [
        "Harry Potter",
        "Hermione Granger",
        "Ron Weasley",
        "Draco Malfoy",
        "Albus Dumbledore"
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
