from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Session(Base):
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id = Column(String, primary_key=True)
    company_uuid = Column(UUID(as_uuid=True), ForeignKey('companies.company_uuid'))
    openai_thread_id = Column(String, unique=True, nullable=False)
    openai_assistant_id = Column(String, nullable=False)
    last_message_at = Column(DateTime(timezone=True))
    
    company = relationship("Company", back_populates="sessions", foreign_keys=[company_uuid])
