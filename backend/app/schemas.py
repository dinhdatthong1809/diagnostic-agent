from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    conditions: Optional[str] = None


class PatientOut(PatientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VitalCreate(BaseModel):
    patient_id: int
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    glucose: Optional[float] = None
    heart_rate: Optional[int] = None
    weight: Optional[float] = None


class AlertOut(BaseModel):
    metric: str
    severity: str
    message: str


class VitalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    glucose: Optional[float] = None
    heart_rate: Optional[int] = None
    weight: Optional[float] = None
    severity: str
    alert_notes: Optional[str] = None
    measured_at: datetime


class VitalResponse(BaseModel):
    record: VitalOut
    alerts: List[AlertOut]


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    answer: str
    sources: List[str]


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime
