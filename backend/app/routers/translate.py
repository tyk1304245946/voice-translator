from fastapi import APIRouter, HTTPException
from app.schemas import TranslateRequest, TranslateResponse
from app.services.translation import translate_text

router = APIRouter()


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        translated = await translate_text(request.text, request.mode)
        return TranslateResponse(translated=translated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
