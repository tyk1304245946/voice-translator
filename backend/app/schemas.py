from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TranslateRequest(BaseModel):
    text: str
    mode: str = "normal"  # "normal" | "short_video"


class TranslateResponse(BaseModel):
    translated: str


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: str


class GenerateRequest(BaseModel):
    texts: List[str]
    mode: str = "normal"
    voice_id: Optional[str] = None


class GenerateItem(BaseModel):
    id: int
    original: str
    translated: str
    audio_url: str
    download_name: str


class GenerateResponse(BaseModel):
    results: List[GenerateItem]


class HistoryItemSchema(BaseModel):
    id: int
    original_text: str
    translated_text: str
    audio_filename: Optional[str] = None
    download_name: Optional[str] = None
    mode: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeishuSyncRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=200)
    mode: str = "short_video"
    voice_id: Optional[str] = None
    audio_only: bool = False


class FeishuSyncResponse(BaseModel):
    scanned: int
    processed: int
    downgraded: int
    skipped: int
    failed: int
    errors: List[str] = Field(default_factory=list)


class FeishuPollingConfigResponse(BaseModel):
    enabled: bool
    interval_seconds: int
    batch_size: int


class FeishuPollingConfigUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    interval_seconds: Optional[int] = Field(default=None, ge=5, le=3600)
    batch_size: Optional[int] = Field(default=None, ge=1, le=200)
