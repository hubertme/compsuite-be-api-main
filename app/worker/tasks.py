from typing import Any, Dict
import structlog

from app.worker.celery_app import celery_app
from app.utils.log_util import get_correlation_id

logger = structlog.get_logger()

@celery_app.task(bind=True)
def example_task(self, correlation_id: str = None, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Example task that demonstrates proper task setup with logging."""
    logger.info(
        "example_task_started",
        correlation_id=correlation_id or get_correlation_id(),
        task_id=self.request.id,
        kwargs=kwargs,
    )
    
    try:
        # Task implementation here
        result = {"status": "success", "message": "Task completed successfully"}
        
        logger.info(
            "example_task_completed",
            correlation_id=correlation_id or get_correlation_id(),
            task_id=self.request.id,
            result=result,
        )
        return result
    
    except Exception as e:
        logger.error(
            "example_task_failed",
            correlation_id=correlation_id or get_correlation_id(),
            task_id=self.request.id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
