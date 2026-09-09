from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(String, nullable=True)
    conditions = Column(String, nullable=True)  # vd: "tang huyet ap, dai thao duong"
    created_at = Column(DateTime, default=datetime.utcnow)

    vitals = relationship("VitalRecord", back_populates="patient", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="patient", cascade="all, delete-orphan")


class VitalRecord(Base):
    __tablename__ = "vital_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)
    glucose = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    severity = Column(String, default="normal")  # normal | info | warning | danger
    alert_notes = Column(Text, nullable=True)
    measured_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="vitals")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="messages")
