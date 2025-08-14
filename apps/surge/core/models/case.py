from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False)
    surgery_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    pre_op_notes = Column(Text, nullable=True)
    post_op_notes = Column(Text, nullable=True)
