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

    # Feishu / Bitable
    feishu_app_id: str = ""
    feishu_app_secret: str = Field(
        default="",
        validation_alias=AliasChoices("FEISHU_APP_SECRET", "FEISHU_TOKEN"),
    )
    feishu_bitable_app_token: str = ""
    feishu_table_id: str = ""
    feishu_chinese_field: str = "中文脚本"
    feishu_english_field: str = "英文脚本"
    feishu_audio_field: str = "音频"
    feishu_poll_enabled: bool = False
    feishu_poll_interval_seconds: int = 60
    feishu_batch_size: int = 3
    feishu_translate_mode: str = "short_video"
    feishu_voice_id: str = ""
    feishu_fallback_text_only_on_audio_fail: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
