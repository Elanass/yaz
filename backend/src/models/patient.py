from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    tumor_staging = relationship("TumorStaging", back_populates="patient")
    treatment_history = relationship("TreatmentHistory", back_populates="patient")
    clinical_outcomes = relationship("ClinicalOutcome", back_populates="patient")
