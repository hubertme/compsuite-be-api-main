import logging
import sys
import uuid
from typing import Any, Dict
from contextvars import ContextVar
import json

import structlog
from structlog.types import Processor

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def add_correlation_id(logger: structlog.BoundLogger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to structured logging."""
    if "correlation_id" not in event_dict:
        try:
            event_dict["correlation_id"] = correlation_id.get()
        except LookupError:
            event_dict["correlation_id"] = str(uuid.uuid4())
    return event_dict

def setup_logging() -> None:
    """Configure structured logging with correlation IDs and proper formatting."""
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_correlation_id,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(serializer=json.dumps)
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Also set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Redirect standard library logging to structlog
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer()
    ))
    logging.getLogger().handlers = [handler]

    # logging.getLogger().handlers = [
    #     structlog.stdlib.ProcessorFormatter(
    #         processor=structlog.dev.ConsoleRenderer(),
    #     )
    # ]

def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    try:
        return correlation_id.get()
    except LookupError:
        return str(uuid.uuid4())

def set_correlation_id(new_id: str = None) -> str:
    """Set a new correlation ID or generate one."""
    new_correlation_id = new_id or str(uuid.uuid4())
    correlation_id.set(new_correlation_id)
    return new_correlation_id
