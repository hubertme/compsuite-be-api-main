from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
import bcrypt
import secrets

class CompanyAPIKey(Base):
    __tablename__ = 'company_api_keys'
    
    id = Column(String, primary_key=True)
    company_uuid = Column(UUID(as_uuid=True), ForeignKey('companies.company_uuid'), nullable=False)
    hashed_key = Column(String, nullable=False)  # BCrypt hash length
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="api_keys")

    def generate_key(self, prefix: str = "sk-") -> str:
        """Generate a random API key with prefix and ID"""
        secret_part = secrets.token_urlsafe(32)
        return f"{prefix}{self.id}.{secret_part}"

    @classmethod
    def parse_key(cls, full_key: str) -> tuple[str, str]:
        """Split key into (id_part, secret_part)"""
        if not full_key.startswith("sk-"):
            raise ValueError("Invalid key prefix")
        id_part, secret_part = full_key[3:].split(".", 1)
        return id_part, secret_part

    @staticmethod
    def hash_key(secret_part: str) -> str:
        """Hash secret part using bcrypt"""
        try:
            encoded_secret = secret_part.encode('utf-8')
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(encoded_secret, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to hash key: {str(e)}")

    def verify_secret(self, secret_part: str) -> bool:
        """Verify API key secret part against stored hash"""
        try:
            # Make sure we have valid inputs for bcrypt
            encoded_secret = secret_part.encode('utf-8')
            encoded_hash = self.hashed_key.encode('utf-8')
            
            return bcrypt.checkpw(encoded_secret, encoded_hash)
        except Exception:
            return False
