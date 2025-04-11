from app.models.session import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.utils.openai_util import OpenAIUtil
import uuid
from datetime import datetime
from openai.types.beta.threads import Message
from typing import List

class SessionService:
    @classmethod
    def __format_openai_messages(cls, raw_messages: List[Message]):
        formatted_messages = []
        for msg in raw_messages:
            message_dict = {
                "id": msg.id,
                "role": msg.role,
                "content": [content.text.value for content in msg.content if hasattr(content, "text")],
                "created_at": msg.created_at
            }
            formatted_messages.append(message_dict)
        return formatted_messages

    @classmethod
    async def create_new_session(cls, db: AsyncSession, company_uuid: str) -> Session:
        """
        Create a new conversation for the given company UUID.
        """
        thread = OpenAIUtil.create_thread()
        session = Session(
            id=str(uuid.uuid4()),
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
    
    @classmethod
    async def close_session(cls, db: AsyncSession, company_uuid: str, session_id: str) -> Session:
        """
        Close the conversation for the given session ID.
        """
        stmt = select(Session).where(
            and_(
                Session.id == session_id,
                Session.company_uuid == company_uuid,
                Session.openai_thread_id.isnot(None),
                Session.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        session = result.scalars().first()

        if session:
            thread = OpenAIUtil.close_thread(session.openai_thread_id)
            session.deleted_at = datetime.now()
            await db.commit()
        else:
            raise Exception("Session not found or already closed.")
            
        return None
    
    @classmethod
    async def get_session_messages(cls, db: AsyncSession, company_uuid: str, session_id: str):
        """
        Get all messages for the given session ID.
        """
        stmt = select(Session).where(
            and_(
                Session.id == session_id,
                Session.company_uuid == company_uuid,
                Session.openai_thread_id.isnot(None),
                Session.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        session = result.scalars().first()

        if session:
            raw_messages = OpenAIUtil.get_all_messages_from_thread(session.openai_thread_id, False)
            return cls.__format_openai_messages(raw_messages)
        else:
            raise Exception("Session not found or already closed.")
    
    @classmethod
    async def send_new_message_to_thread(cls, db: AsyncSession, company_uuid: str, session_id: str, content: str) -> List[Message]:
        """
        Send a new message to the given session ID.
        """
        stmt = select(Session).where(
            and_(
                Session.id == session_id,
                Session.company_uuid == company_uuid,
                Session.openai_thread_id.isnot(None),
                Session.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        session = result.scalars().first()
        if not session:
            raise Exception("Session not found or already closed.")
        
        OpenAIUtil.add_message_to_thread(session.openai_thread_id, content)
        session.last_message_at = datetime.now()

        assistant_id = "asst_RFkSdaaZovJ9CWznwwfI2lPm"
        messages = OpenAIUtil.run_assistant(session.openai_thread_id, assistant_id)
        session.last_message_at = datetime.now()

        await db.commit()
        return cls.__format_openai_messages(messages)