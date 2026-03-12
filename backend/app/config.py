from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    # Rachel — 免费可用的默认声音
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    database_url: str = "sqlite:///./translator.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
