from datetime import datetime
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Query

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate plural __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        name = cls.__name__.lower()
        if name.endswith('y'):
            return name[:-1] + 'ies'
        return name + 's'

    # Add timestamp columns to all tables
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Filter out deleted records by default
    @classmethod
    def query(cls) -> Query:
        return super().query().filter(cls.deleted_at == None)
