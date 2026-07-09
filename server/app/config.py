from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    app_name: str = "Job Scraper"
    debug: bool = False
    database_url: str = "sqlite:///./data.db"
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
