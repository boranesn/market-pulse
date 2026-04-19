from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MARKET_PULSE_", env_file=".env", extra="ignore")

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    alpha_vantage_api_key: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    news_api_key: str = Field(default="", alias="NEWS_API_KEY")
    reddit_client_id: str = Field(default="", alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default="", alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="market-pulse/1.0", alias="REDDIT_USER_AGENT")

    slack_webhook_url: str = Field(default="", alias="SLACK_WEBHOOK_URL")
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")

    db_path: Path = Path.home() / ".market-pulse" / "data.duckdb"
    cache_dir: Path = Path.home() / ".market-pulse" / "cache"

    claude_model: str = "claude-sonnet-4-6"
    request_timeout: int = 30
    cache_ttl_seconds: int = 300


settings = Settings()
