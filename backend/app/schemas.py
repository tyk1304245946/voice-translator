from pydantic import BaseModel
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


class GenerateResponse(BaseModel):
    results: List[GenerateItem]


class HistoryItemSchema(BaseModel):
    id: int
    original_text: str
    translated_text: str
    audio_filename: Optional[str] = None
    mode: str
    created_at: datetime

    model_config = {"from_attributes": True}
