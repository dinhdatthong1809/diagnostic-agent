from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.routers.patients import get_patient_or_404
from app.rag.chain import ask, format_patient_summary

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{patient_id}", response_model=schemas.ChatOut)
def chat(patient_id: int, payload: schemas.ChatIn, db: Session = Depends(get_db)):
    patient = get_patient_or_404(db, patient_id)

    recent_vitals = (
        db.query(models.VitalRecord)
        .filter(models.VitalRecord.patient_id == patient_id)
        .order_by(models.VitalRecord.measured_at.desc())
        .limit(5)
        .all()
    )
    patient_summary = format_patient_summary(patient, recent_vitals)

    history_rows = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.patient_id == patient_id)
        .order_by(models.ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    chat_history = [{"role": m.role, "content": m.content} for m in reversed(history_rows)]

    answer, sources = ask(payload.message, patient_summary, chat_history)

    db.add(models.ChatMessage(patient_id=patient_id, role="user", content=payload.message))
    db.add(models.ChatMessage(patient_id=patient_id, role="assistant", content=answer))
    db.commit()

    return {"answer": answer, "sources": sources}


@router.get("/{patient_id}", response_model=List[schemas.ChatMessageOut])
def get_chat_history(patient_id: int, db: Session = Depends(get_db)):
    get_patient_or_404(db, patient_id)
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.patient_id == patient_id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )
