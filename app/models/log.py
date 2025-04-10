from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    severity = Column(String)
    module = Column(String)
    function_name = Column(String)
    message = Column(String)
    data = Column(JSON)
    user_uid = Column(String)

    def __repr__(self):
        return f"<Log(id={self.id}, severity={self.severity}, module={self.module})>"