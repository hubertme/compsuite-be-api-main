from openai import OpenAI
from app.config.app_config import settings
from openai.types.beta import Thread
from openai.types.beta.threads import Message
from typing import List
import time

class OpenAIUtil:
    __client = None

    @classmethod
    def init(cls):
        if cls.__client is None:
            cls.__client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return
    
    @classmethod
    def create_thread(cls) -> Thread:
        """Create a new thread for a conversation."""
        thread = cls.__client.beta.threads.create()
        return thread
    
    @classmethod
    def close_thread(cls, thread_id: str) -> Thread:
        """Close the thread."""
        thread = cls.__client.beta.threads.delete(thread_id=thread_id)
        return thread
    
    @classmethod
    def get_all_messages_from_thread(cls, thread_id: str, is_reverse: bool = True) -> List[Message]:
        """Get all messages from a thread."""
        messages = cls.__client.beta.threads.messages.list(thread_id=thread_id, order="desc" if is_reverse else "asc")
        return messages.data
    
    @classmethod
    def run_assistant(cls, thread_id: str, assistant_id: str) -> List[Message]:
        """Run the Assistant on the thread and get the response."""
        # Create a run
        run = cls.__client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        
        # Poll the run status until it's completed
        while True:
            run_status = cls.__client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)
        
        # Retrieve the latest message from the thread (Assistant's response)
        messages = cls.get_all_messages_from_thread(thread_id, is_reverse=False)
        if len(messages) <= 0:
            raise Exception("No messages found in the thread.")
        
        return messages
    
    @classmethod
    def add_message_to_thread(cls, thread_id, content):
        """Add a user message to the thread."""
        message = cls.__client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return message