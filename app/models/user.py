from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, is_active={self.is_active}, is_superuser={self.is_superuser})"
