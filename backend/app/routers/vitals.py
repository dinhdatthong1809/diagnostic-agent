import json
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, thresholds
from app.routers.patients import get_patient_or_404

router = APIRouter(prefix="/vitals", tags=["vitals"])


@router.post("/", response_model=schemas.VitalResponse)
def add_vital(payload: schemas.VitalCreate, db: Session = Depends(get_db)):
    get_patient_or_404(db, payload.patient_id)

    alerts = thresholds.evaluate_all(
        systolic=payload.systolic,
        diastolic=payload.diastolic,
        glucose=payload.glucose,
        heart_rate=payload.heart_rate,
    )
    severity = thresholds.worst_severity(alerts)

    record = models.VitalRecord(
        patient_id=payload.patient_id,
        systolic=payload.systolic,
        diastolic=payload.diastolic,
        glucose=payload.glucose,
        heart_rate=payload.heart_rate,
        weight=payload.weight,
        severity=severity,
        alert_notes=json.dumps(alerts, ensure_ascii=False) if alerts else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"record": record, "alerts": alerts}


@router.get("/{patient_id}", response_model=List[schemas.VitalOut])
def list_vitals(patient_id: int, db: Session = Depends(get_db)):
    get_patient_or_404(db, patient_id)
    return (
        db.query(models.VitalRecord)
        .filter(models.VitalRecord.patient_id == patient_id)
        .order_by(models.VitalRecord.measured_at.asc())
        .all()
    )
