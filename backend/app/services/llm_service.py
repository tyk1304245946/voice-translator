from openai import AsyncOpenAI
from app.config import settings

ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
ARK_MODEL = "ark-code-latest"

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.ark_api_key,
            base_url=ARK_BASE_URL,
        )
    return _client


async def create_chat_completion(messages: list[dict], temperature: float = 0.3):
    client = get_llm_client()
    return await client.chat.completions.create(
        model=ARK_MODEL,
        messages=messages,
        temperature=temperature,
    )
