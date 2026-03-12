from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import (
    TTSRequest,
    TTSResponse,
    GenerateRequest,
    GenerateResponse,
    GenerateItem,
)
from app.services.elevenlabs_service import generate_audio
from app.services.translation import translate_text
from app.database import get_db, HistoryRecord

router = APIRouter()


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        filename = await generate_audio(request.text, request.voice_id)
        return TTSResponse(audio_url=f"/audio/{filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, db: Session = Depends(get_db)):
    texts = [t.strip() for t in request.texts if t.strip()]
    if not texts:
        raise HTTPException(status_code=400, detail="No non-empty texts provided")

    results = []
    for text in texts:
        try:
            translated = await translate_text(text, request.mode)
            filename = await generate_audio(translated, request.voice_id)

            record = HistoryRecord(
                original_text=text,
                translated_text=translated,
                audio_filename=filename,
                mode=request.mode,
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            results.append(
                GenerateItem(
                    id=record.id,
                    original=text,
                    translated=translated,
                    audio_url=f"/audio/{filename}",
                )
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process text #{len(results) + 1}: {str(e)}",
            )

    return GenerateResponse(results=results)
