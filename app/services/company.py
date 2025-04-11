from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.models.company import Company
from app.models.company_api_key import CompanyAPIKey
from app.schemas.company import CreateCompanyRequest
from datetime import datetime
import uuid
import secrets

class CompanyService:
    @classmethod
    async def create_company(cls, db: AsyncSession, req: CreateCompanyRequest):
        # Create company
        company_uuid = uuid.uuid4()
        company = Company(
            company_uuid=company_uuid,
            company_name=req.company_name,
            display_name=req.display_name or req.company_name,
            is_active=True
        )
        
        db.add(company)
        await db.flush()
        
        # Create an API key for the company
        api_key_record = CompanyAPIKey(
            id=secrets.token_urlsafe(26),
            company_uuid=company_uuid,
            name="Default API Key"
        )
        api_key = api_key_record.generate_key()
        
        # Hash the secret part
        _, secret_part = CompanyAPIKey.parse_key(api_key)
        api_key_record.hashed_key = CompanyAPIKey.hash_key(secret_part)
        
        db.add(api_key_record)
        await db.commit()
        await db.refresh(company)
        
        # Return company info along with the API key
        return {
            "company_uuid": str(company.company_uuid),
            "company_name": company.company_name,
            "display_name": company.display_name,
            "is_active": company.is_active,
            "api_key": api_key
        }
    
    @classmethod
    async def get_company_by_api_key(cls, db: AsyncSession, api_key: str) -> Company:
        """
        Retrieve a company by validating the provided API key
        
        Args:
            db: AsyncSession - The database session
            api_key: str - The full API key (format: sk-[id].[secret])
            
        Returns:
            Company or None - The company if the API key is valid, None otherwise
        """
        try:
            # Parse the key to get the ID part
            key_id, key_secret = CompanyAPIKey.parse_key(api_key)
            
            # Get the API key record by ID
            stmt = select(CompanyAPIKey).where(
                and_(
                    CompanyAPIKey.id == key_id,
                    CompanyAPIKey.revoked_at.is_(None)
                )
            )
            result = await db.execute(stmt)
            api_key_record = result.scalars().first()
            
            if not api_key_record:
                return None
            
            verification_result = api_key_record.verify_secret(key_secret)
            
            if not verification_result:
                return None
            
            # Fetch the company
            stmt = select(Company).where(Company.company_uuid == api_key_record.company_uuid)
            result = await db.execute(stmt)
            return result.scalars().first()
        
        except ValueError:
            return None
        except Exception:
            return None

    @classmethod
    async def get_company_by_uuid(cls, db: AsyncSession, company_uuid: str) -> Company:
        """
        Retrieve a company by its UUID
        
        Args:
            db: AsyncSession - The database session
            company_uuid: uuid.UUID - The UUID of the company
            
        Returns:
            Company or None - The company if found, None otherwise
        """
        stmt = select(Company).where(Company.company_uuid == company_uuid)
        result = await db.execute(stmt)
        return result.scalars().first()
