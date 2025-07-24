from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TumorStaging(Base):
    __tablename__ = 'tumor_staging'

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(String, nullable=False)
    description = Column(String, nullable=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    patient = relationship("Patient", back_populates="tumor_staging")
