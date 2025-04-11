from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Session(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_uuid = Column(UUID(as_uuid=True), ForeignKey('companies.company_uuid'))
    openai_thread_id = Column(String, unique=True, nullable=False)
    company = relationship("Company", back_populates="sessions", foreign_keys=[company_uuid])

    class Config:
        from_attributes = True  # Allows mapping from SQLAlchemy objects
