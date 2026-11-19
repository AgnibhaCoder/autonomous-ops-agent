import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Ops Agent"
    DATABASE_URL: str ="postgresql+asyncpg://postgres:postgres@localhost:5433/agent_db"
    OPENAI_API_KEY: str = ""
    MAX_AGENT_STEPS: int = 10
    TOOL_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()