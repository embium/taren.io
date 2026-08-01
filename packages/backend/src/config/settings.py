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
    openrouter_model: str = "deepseek/deepseek-v4-flash"
    proxy_url: str = "http://proxy.proxying.io:8080"
    scrape_limit: int = 25

    # Stripe settings
    stripe_product_id_starter: str = "prod_UzilBzFZtKK3ms"
    stripe_product_id_professional: str = "prod_UzilBzFZtKK3ms"


# Global settings instance
settings = Settings()
