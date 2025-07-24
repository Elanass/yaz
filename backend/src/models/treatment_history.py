from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class TreatmentHistory(Base):
    __tablename__ = 'treatment_history'

    id = Column(Integer, primary_key=True, index=True)
    treatment_name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    patient = relationship("Patient", back_populates="treatment_history")
