from app.models.session import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.utils.openai_util import OpenAIUtil

class SessionService:
    @classmethod
    async def create_new_session(cls, db: AsyncSession, company_uuid: str) -> Session:
        """
        Create a new conversation for the given company UUID.
        """
        thread = OpenAIUtil.create_thread()
        session = Session(
            company_uuid=company_uuid,
            openai_thread_id=thread.id,
        )
        db.add(session)
        await db.flush()
        await db.commit()

        return session

    @classmethod
    async def get_all_sessions(cls, db: AsyncSession, company_uuid: str) -> list[Session]:
        """
        Get all conversations for the given company UUID.
        """
        stmt = select(Session).where(
            and_(
                Session.company_uuid == company_uuid,
                Session.openai_thread_id.isnot(None),
                Session.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        return sessions
