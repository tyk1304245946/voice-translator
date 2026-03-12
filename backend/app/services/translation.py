from openai import AsyncOpenAI
from app.config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


NORMAL_SYSTEM_PROMPT = (
    "You are a professional translator. "
    "Translate the Chinese text to natural, fluent English. "
    "Preserve the original meaning and tone. "
    "Output only the translated text, nothing else."
)

SHORT_VIDEO_SYSTEM_PROMPT = (
    "You are a professional translator specializing in short-form video scripts. "
    "Translate the Chinese text to English following these guidelines:\n"
    "1. Keep each sentence concise (8-12 words max)\n"
    "2. Use casual, conversational language\n"
    "3. Make it punchy and engaging for social media viewers\n"
    "4. Ensure it is easy to pronounce naturally\n"
    "5. Break complex ideas into shorter, snappier sentences\n"
    "Output only the translated text, nothing else."
)


async def translate_text(text: str, mode: str = "normal") -> str:
    client = get_client()
    system_prompt = (
        SHORT_VIDEO_SYSTEM_PROMPT if mode == "short_video" else NORMAL_SYSTEM_PROMPT
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
