from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Kiliwvatg Bot API"
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    telegram_bot_token: str = ""


settings = Settings()
