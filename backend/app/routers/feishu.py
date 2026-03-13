from fastapi import APIRouter, HTTPException

from app.schemas import (
    FeishuPollingConfigResponse,
    FeishuPollingConfigUpdateRequest,
    FeishuSyncRequest,
    FeishuSyncResponse,
)
from app.services.feishu_bitable_service import (
    get_polling_config,
    sync_bitable_once,
    update_polling_config,
)

router = APIRouter()


@router.post("/feishu/sync", response_model=FeishuSyncResponse)
async def sync_feishu_bitable(request: FeishuSyncRequest):
    try:
        result = await sync_bitable_once(
            limit=request.limit,
            mode=request.mode,
            voice_id=request.voice_id,
            audio_only=request.audio_only,
        )
        return FeishuSyncResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/feishu/polling-config", response_model=FeishuPollingConfigResponse)
async def get_feishu_polling_config():
    return FeishuPollingConfigResponse(**get_polling_config())


@router.patch("/feishu/polling-config", response_model=FeishuPollingConfigResponse)
async def patch_feishu_polling_config(request: FeishuPollingConfigUpdateRequest):
    try:
        result = await update_polling_config(
            enabled=request.enabled,
            interval_seconds=request.interval_seconds,
            batch_size=request.batch_size,
        )
        return FeishuPollingConfigResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
