import asyncio
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.config import settings
from app.services.elevenlabs_service import generate_audio
from app.services.translation import translate_text

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

logger = logging.getLogger(__name__)


class FeishuClientError(Exception):
    pass


class FeishuClient:
    def __init__(self) -> None:
        self._tenant_access_token: str = ""
        self._token_expire_at: datetime | None = None

    async def _ensure_tenant_access_token(self) -> str:
        now = datetime.now(timezone.utc)
        if (
            self._tenant_access_token
            and self._token_expire_at is not None
            and now < self._token_expire_at
        ):
            return self._tenant_access_token

        if not settings.feishu_app_id or not settings.feishu_app_secret:
            raise FeishuClientError("Missing FEISHU_APP_ID or FEISHU_APP_SECRET")

        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": settings.feishu_app_id,
            "app_secret": settings.feishu_app_secret,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if data.get("code") != 0:
            raise FeishuClientError(
                f"Failed to get tenant access token: {data.get('msg', 'unknown error')}"
            )

        token = data.get("tenant_access_token")
        expire = int(data.get("expire", 7200))
        if not token:
            raise FeishuClientError("Empty tenant_access_token from Feishu")

        self._tenant_access_token = token
        # Keep 60 seconds buffer to avoid expiry during requests.
        self._token_expire_at = now + timedelta(seconds=max(expire - 60, 60))
        return token

    async def _authorized_headers(self) -> dict[str, str]:
        token = await self._ensure_tenant_access_token()
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _extract_error_message(data: dict[str, Any], fallback: str) -> str:
        details = data.get("error") or {}
        details_msg = details.get("message") if isinstance(details, dict) else ""
        msg = data.get("msg") or details_msg or fallback
        code = data.get("code")
        if code is None:
            return str(msg)
        return f"code={code}, msg={msg}"

    async def list_records(
        self, page_size: int = 200, page_token: str | None = None
    ) -> dict[str, Any]:
        if not settings.feishu_bitable_app_token or not settings.feishu_table_id:
            raise FeishuClientError(
                "Missing FEISHU_BITABLE_APP_TOKEN or FEISHU_TABLE_ID"
            )

        url = (
            f"{FEISHU_BASE_URL}/bitable/v1/apps/{settings.feishu_bitable_app_token}"
            f"/tables/{settings.feishu_table_id}/records"
        )
        params: dict[str, Any] = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token

        headers = await self._authorized_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            data = resp.json()

        if resp.status_code >= 400 or data.get("code") != 0:
            raise FeishuClientError(
                "Failed to list records: "
                + self._extract_error_message(data, f"http_status={resp.status_code}")
            )
        return data.get("data", {})

    async def list_fields(self) -> list[dict[str, Any]]:
        url = (
            f"{FEISHU_BASE_URL}/bitable/v1/apps/{settings.feishu_bitable_app_token}"
            f"/tables/{settings.feishu_table_id}/fields"
        )

        headers = await self._authorized_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers, params={"page_size": 200})
            data = resp.json()

        if resp.status_code >= 400 or data.get("code") != 0:
            raise FeishuClientError(
                "Failed to list fields: "
                + self._extract_error_message(data, f"http_status={resp.status_code}")
            )

        return data.get("data", {}).get("items", [])

    async def update_record(self, record_id: str, fields: dict[str, Any]) -> None:
        url = (
            f"{FEISHU_BASE_URL}/bitable/v1/apps/{settings.feishu_bitable_app_token}"
            f"/tables/{settings.feishu_table_id}/records/{record_id}"
        )
        payload = {"fields": fields}

        headers = await self._authorized_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.put(url, headers=headers, json=payload)
            data = resp.json()

        if resp.status_code >= 400 or data.get("code") != 0:
            raise FeishuClientError(
                f"Failed to update record {record_id}: "
                + self._extract_error_message(data, f"http_status={resp.status_code}")
            )

    async def upload_audio(self, local_file_path: str, upload_name: str) -> str:
        if not os.path.exists(local_file_path):
            raise FeishuClientError(f"Audio file not found: {local_file_path}")

        url = f"{FEISHU_BASE_URL}/drive/v1/medias/upload_all"
        headers = await self._authorized_headers()

        file_size = os.path.getsize(local_file_path)
        data = {
            "file_name": upload_name,
            "parent_type": "bitable_file",
            "parent_node": settings.feishu_bitable_app_token,
            "size": str(file_size),
        }

        with open(local_file_path, "rb") as file_obj:
            files = {"file": (upload_name, file_obj, "audio/mpeg")}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, data=data, files=files)
                payload = resp.json()

        if resp.status_code >= 400 or payload.get("code") != 0:
            raise FeishuClientError(
                "Failed to upload audio: "
                + self._extract_error_message(payload, f"http_status={resp.status_code}")
            )

        file_token = payload.get("data", {}).get("file_token")
        if not file_token:
            raise FeishuClientError("Upload succeeded but file_token is missing")

        return file_token


_client = FeishuClient()
_polling_task: asyncio.Task | None = None
_polling_enabled = settings.feishu_poll_enabled
_polling_interval_seconds = max(5, settings.feishu_poll_interval_seconds)
_polling_batch_size = max(1, settings.feishu_batch_size)


def _sanitize_multiline_text(value: str) -> str:
    # Remove unsupported control chars except line breaks and tabs.
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)
    return cleaned.strip()


async def _resolve_field_ids() -> dict[str, str]:
    fields = await _client.list_fields()
    by_name = {f.get("field_name"): f for f in fields}

    cn = by_name.get(settings.feishu_chinese_field)
    en = by_name.get(settings.feishu_english_field)
    audio = by_name.get(settings.feishu_audio_field)

    missing = []
    if not cn:
        missing.append(settings.feishu_chinese_field)
    if not en:
        missing.append(settings.feishu_english_field)
    if not audio:
        missing.append(settings.feishu_audio_field)
    if missing:
        raise FeishuClientError(f"Configured fields not found: {', '.join(missing)}")

    audio_ui_type = str(audio.get("ui_type") or "")
    if audio_ui_type.lower() != "attachment":
        raise FeishuClientError(
            f"Field '{settings.feishu_audio_field}' must be Attachment, got {audio_ui_type}"
        )

    return {
        "cn_id": str(cn.get("field_id")),
        "en_id": str(en.get("field_id")),
        "audio_id": str(audio.get("field_id")),
    }


def _extract_text(cell_value: Any) -> str:
    if cell_value is None:
        return ""
    if isinstance(cell_value, str):
        return cell_value.strip()
    if isinstance(cell_value, (int, float)):
        return str(cell_value).strip()
    if isinstance(cell_value, list):
        parts: list[str] = []
        for item in cell_value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("name")
                if text:
                    parts.append(str(text))
        return " ".join(parts).strip()
    if isinstance(cell_value, dict):
        text = cell_value.get("text") or cell_value.get("name")
        return str(text).strip() if text else ""
    return str(cell_value).strip()


def _has_audio_attachments(cell_value: Any) -> bool:
    if cell_value is None:
        return False
    if isinstance(cell_value, list):
        return len(cell_value) > 0
    if isinstance(cell_value, dict):
        return bool(cell_value)
    return bool(str(cell_value).strip())


async def sync_bitable_once(
    limit: int,
    mode: str | None = None,
    voice_id: str | None = None,
    audio_only: bool = False,
) -> dict[str, Any]:
    scan_count = 0
    attempted = 0
    processed = 0
    downgraded = 0
    skipped = 0
    failed = 0
    errors: list[str] = []

    if limit <= 0:
        return {
            "scanned": scan_count,
            "processed": processed,
            "downgraded": downgraded,
            "skipped": skipped,
            "failed": failed,
            "errors": errors,
        }

    field_ids = await _resolve_field_ids()

    page_token: str | None = None
    while True:
        data = await _client.list_records(page_size=200, page_token=page_token)
        items = data.get("items", [])

        if not items:
            break

        for item in items:
            if attempted >= limit:
                break

            scan_count += 1
            record_id = item.get("record_id", "")
            fields = item.get("fields", {})

            cn_text = _extract_text(fields.get(settings.feishu_chinese_field))
            en_text = _extract_text(fields.get(settings.feishu_english_field))
            has_audio = _has_audio_attachments(fields.get(settings.feishu_audio_field))

            # Process only records that have Chinese text and still need either
            # English translation or audio attachment.
            if not cn_text or (en_text and has_audio):
                skipped += 1
                continue

            # Audio-only mode never translates missing English text.
            if audio_only and not en_text:
                skipped += 1
                continue

            attempted += 1
            local_audio_path = ""
            translated = en_text
            try:
                if not translated:
                    translated = await translate_text(
                        cn_text,
                        mode or settings.feishu_translate_mode,
                    )
                translated = _sanitize_multiline_text(translated)
                if not translated:
                    raise FeishuClientError(
                        "Translated text is empty after sanitization"
                    )
                audio_name = await generate_audio(
                    translated,
                    voice_id or settings.feishu_voice_id or None,
                )
                local_audio_path = f"audio/{audio_name}"

                file_token = await _client.upload_audio(local_audio_path, audio_name)
                update_fields: dict[str, Any] = {
                    field_ids["audio_id"]: [{"file_token": file_token}],
                }
                if not en_text:
                    update_fields[field_ids["en_id"]] = translated
                await _client.update_record(
                    record_id,
                    update_fields,
                )
                processed += 1
            except Exception as exc:
                can_fallback = (
                    settings.feishu_fallback_text_only_on_audio_fail
                    and not en_text
                    and bool(translated)
                )
                if can_fallback:
                    try:
                        await _client.update_record(
                            record_id,
                            {
                                field_ids["en_id"]: translated,
                            },
                        )
                        processed += 1
                        downgraded += 1
                        errors.append(
                            f"record={record_id}: audio failed, filled translation only: {exc}"
                        )
                    except Exception as fallback_exc:
                        failed += 1
                        errors.append(
                            f"record={record_id}: audio failed ({exc}); "
                            f"fallback update failed ({fallback_exc})"
                        )
                        logger.exception(
                            "Failed to sync Feishu record %s (fallback failed)",
                            record_id,
                        )
                else:
                    failed += 1
                    errors.append(f"record={record_id}: {exc}")
                    logger.exception("Failed to sync Feishu record %s", record_id)
            finally:
                if local_audio_path and os.path.exists(local_audio_path):
                    os.remove(local_audio_path)

        if attempted >= limit:
            break

        if not data.get("has_more"):
            break
        page_token = data.get("page_token")

    return {
        "scanned": scan_count,
        "processed": processed,
        "downgraded": downgraded,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
    }


async def _poll_loop() -> None:
    while True:
        try:
            batch_size = _polling_batch_size
            result = await sync_bitable_once(limit=batch_size)
            if result["processed"] or result["failed"]:
                logger.info("Feishu poll sync result: %s", result)
        except Exception:
            logger.exception("Feishu polling failed")

        interval = _polling_interval_seconds
        await asyncio.sleep(interval)


async def start_feishu_polling() -> None:
    global _polling_task

    if not _polling_enabled:
        logger.info("Feishu polling is disabled by FEISHU_POLL_ENABLED")
        return
    if _polling_task and not _polling_task.done():
        return

    _polling_task = asyncio.create_task(_poll_loop())
    logger.info("Feishu polling started")


async def stop_feishu_polling() -> None:
    global _polling_task

    if not _polling_task:
        return

    _polling_task.cancel()
    try:
        await _polling_task
    except asyncio.CancelledError:
        pass
    finally:
        _polling_task = None


def get_polling_config() -> dict[str, Any]:
    return {
        "enabled": _polling_enabled,
        "interval_seconds": _polling_interval_seconds,
        "batch_size": _polling_batch_size,
    }


async def update_polling_config(
    enabled: bool | None = None,
    interval_seconds: int | None = None,
    batch_size: int | None = None,
) -> dict[str, Any]:
    global _polling_enabled, _polling_interval_seconds, _polling_batch_size

    if interval_seconds is not None:
        _polling_interval_seconds = max(5, interval_seconds)
    if batch_size is not None:
        _polling_batch_size = max(1, batch_size)
    if enabled is not None:
        _polling_enabled = enabled

    if _polling_enabled:
        await start_feishu_polling()
    else:
        await stop_feishu_polling()

    return get_polling_config()
