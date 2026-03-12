import re
from app.services.llm_service import create_chat_completion


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

DOWNLOAD_NAME_SYSTEM_PROMPT = (
    "你是中文命名助手。请根据文案内容生成一个用于下载音频的中文文件名（不含扩展名）。"
    "要求：6-18个中文字符，简洁自然，体现主题，不要标点，不要空格，不要引号。"
)


async def translate_text(text: str, mode: str = "normal") -> str:
    system_prompt = (
        SHORT_VIDEO_SYSTEM_PROMPT if mode == "short_video" else NORMAL_SYSTEM_PROMPT
    )
    response = await create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def _sanitize_file_stem(stem: str) -> str:
    safe = stem.strip()
    # 兼容常见系统文件名限制，保留中文/英文/数字/下划线/连字符。
    safe = re.sub(r"[\\/:*?\"<>|]", "", safe)
    safe = re.sub(r"\s+", "", safe)
    safe = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9_-]", "", safe)
    return safe[:36] if safe else "中文语音"


async def generate_download_name(original_text: str, translated_text: str) -> str:
    prompt = (
        "请基于以下内容生成中文下载文件名（不带扩展名）：\n"
        f"原文：{original_text}\n"
        f"译文：{translated_text}\n"
        "仅输出文件名本体。"
    )

    response = await create_chat_completion(
        messages=[
            {"role": "system", "content": DOWNLOAD_NAME_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    generated = response.choices[0].message.content or "中文语音"
    return f"{_sanitize_file_stem(generated)}.mp3"
