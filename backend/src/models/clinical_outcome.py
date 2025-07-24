from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class ClinicalOutcome(Base):
    __tablename__ = 'clinical_outcomes'

    id = Column(Integer, primary_key=True, index=True)
    outcome_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    patient = relationship("Patient", back_populates="clinical_outcomes")
