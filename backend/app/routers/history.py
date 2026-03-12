from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
from app.database import get_db, HistoryRecord
from app.schemas import HistoryItemSchema

router = APIRouter()


@router.get("/history", response_model=List[HistoryItemSchema])
def get_history(db: Session = Depends(get_db)):
    return db.query(HistoryRecord).order_by(HistoryRecord.created_at.desc()).all()


@router.delete("/history/{item_id}")
def delete_history_item(item_id: int, db: Session = Depends(get_db)):
    record = db.query(HistoryRecord).filter(HistoryRecord.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.audio_filename:
        filepath = f"audio/{record.audio_filename}"
        if os.path.exists(filepath):
            os.remove(filepath)

    db.delete(record)
    db.commit()
    return {"message": "Deleted successfully"}


@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    records = db.query(HistoryRecord).all()
    for record in records:
        if record.audio_filename:
            filepath = f"audio/{record.audio_filename}"
            if os.path.exists(filepath):
                os.remove(filepath)
    db.query(HistoryRecord).delete()
    db.commit()
    return {"message": "History cleared"}
