"""
Data Models
Essential database models for YAZ platform
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from shared.database import Base
from shared.models import BaseEntity


class User(BaseEntity):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String, default="user")


class Case(BaseEntity):
    """Medical case model"""
    __tablename__ = "cases"
    
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="active", index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship
    user = relationship("User", back_populates="cases")


# Add back_populates to User model
User.cases = relationship("Case", back_populates="user")
    
    user = relationship("User", backref="cases")


class Session(BaseEntity):
    """User session model"""
    __tablename__ = "sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    app_name = Column(String, index=True)
    data = Column(Text)  # JSON data
    
    user = relationship("User", backref="sessions")
