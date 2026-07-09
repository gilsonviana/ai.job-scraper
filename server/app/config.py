from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    app_name: str = "Job Scraper"
    debug: bool = False
    database_url: str = "sqlite:///./data.db"
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    log_level: str = "INFO"
    nlp_model_spacy: str = "en_core_web_lg"
    nlp_model_hf_stack: str = "distilbert-base-uncased-finetuned-sst-2-english"
    nlp_model_hf_classifier: str = "facebook/bart-large-mnli"
    confidence_threshold: float = 0.7
    max_input_size: int = 51200
    extraction_timeout: int = 30
    max_pdf_size: int = 10485760

    class Config:
        env_file = ".env"


settings = Settings()
