import os
from pathlib import Path
from pydantic import BaseSettings, Field, HttpUrl
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    environment: str = Field("production", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    database_url: str = Field("sqlite:///./data/trendbot.db", env="DATABASE_URL")

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o", env="OPENAI_MODEL")

    twitter_api_key: str | None = Field(None, env="TWITTER_API_KEY")
    twitter_api_secret: str | None = Field(None, env="TWITTER_API_SECRET")
    twitter_access_token: str | None = Field(None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: str | None = Field(None, env="TWITTER_ACCESS_SECRET")
    twitter_bearer_token: str | None = Field(None, env="TWITTER_BEARER_TOKEN")

    telegram_bot_token: str | None = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(None, env="TELEGRAM_CHAT_ID")

    cryptopanic_api_key: str | None = Field(None, env="CRYPTOPANIC_API_KEY")
    reddit_user_agent: str = Field("TrendBot/1.0 (+https://github.com)", env="REDDIT_USER_AGENT")

    daily_post_hour: int = Field(9, env="DAILY_POST_HOUR")
    daily_post_minute: int = Field(0, env="DAILY_POST_MINUTE")
    post_frequency_per_day: int = Field(1, env="POST_FREQUENCY_PER_DAY")
    max_trends_per_run: int = Field(3, env="MAX_TRENDS_PER_RUN")

    twitter_enabled: bool = Field(True, env="TWITTER_ENABLED")
    telegram_enabled: bool = Field(True, env="TELEGRAM_ENABLED")

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"

settings = Settings()
