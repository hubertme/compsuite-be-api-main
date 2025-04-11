from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Company(Base):
    id = Column(Integer, primary_key=True, index=True)
    company_uuid = Column(UUID(as_uuid=True), index=True, unique=True)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    display_name = Column(String)
    sessions = relationship("Session", back_populates="company")
    api_keys = relationship("CompanyAPIKey", back_populates="company", cascade="all, delete-orphan")
