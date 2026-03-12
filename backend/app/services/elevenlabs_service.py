import httpx
import uuid
from app.config import settings

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"
TTS_STYLE_PROMPT = (
    "Energetic young male/female, loud, highly persuasive, enthusiastic, "
    "promotional, fast-paced, sales pitch, confident."
)


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
        "prompt": TTS_STYLE_PROMPT,
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
        # 某些 ElevenLabs 版本可能不接受 prompt 字段，遇到参数错误时回退重试。
        if response.status_code in (400, 422):
            fallback_payload = {k: v for k, v in payload.items() if k != "prompt"}
            response = await client.post(
                f"{ELEVENLABS_API_URL}/text-to-speech/{vid}",
                headers=headers,
                json=fallback_payload,
            )
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

    return filename
