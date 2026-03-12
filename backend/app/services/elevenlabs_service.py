import httpx
import uuid
from app.config import settings

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"


async def generate_audio(text: str, voice_id: str | None = None) -> str:
    """
    调用 ElevenLabs TTS API，将文本转为 MP3，保存到 audio/ 目录并返回文件名。
    """
    vid = voice_id or settings.elevenlabs_voice_id
    filename = f"{uuid.uuid4()}.mp3"
    filepath = f"audio/{filename}"

    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ELEVENLABS_API_URL}/text-to-speech/{vid}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

    return filename
