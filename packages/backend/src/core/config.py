"""Configuration settings for the application."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database settings
    database_url: str = "postgresql://user:password@localhost:5432/taren_auth"
    redis_url: str = "redis://localhost:6379"

    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Application settings
    environment: str = "development"
    debug: bool = True
    frontend_url: str = "http://localhost:5173"

    # CORS settings
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # Email settings (Resend)
    resend_api_key: str = ""
    email_from_address: str = "noreply@taren.io"
    email_from_name: str = "Taren"
    app_name: str = "Taren"

    # Email verification settings
    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_hours: int = 1

    # Reddit scraper settings
    openrouter_api_key: str = ""
    openrouter_scraping_model: str = "deepseek/deepseek-v4-flash"
    openrouter_keywords_model: str = "openai/gpt-4o-mini-2024-07-18"
    proxy_url: str = "http://proxy.proxying.io:8080"
    max_concurrent_posts: int = 10

    # Stripe settings
    stripe_publishable_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_product_id_starter: str = ""
    stripe_product_id_professional: str = ""
    stripe_starter_trial_days: int = 7

    # Google OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"


# Global settings instance
settings = Settings()
