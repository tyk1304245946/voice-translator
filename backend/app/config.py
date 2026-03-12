from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field


class Settings(BaseSettings):
    # 优先读取 ARK_API_KEY，兼容历史 OPENAI_API_KEY。
    ark_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("ARK_API_KEY", "OPENAI_API_KEY"),
    )
    elevenlabs_api_key: str = ""
    # Rachel — 免费可用的默认声音
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    database_url: str = "sqlite:///./translator.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
