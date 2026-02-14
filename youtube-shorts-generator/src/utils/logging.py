"""
Structured JSON logging for pipeline and agents.
"""
import logging
import sys
from typing import Any, Optional

import structlog

# Default: JSON to stdout for local dev; can be overridden
def configure_logging(
    level: str = "INFO",
    json_console: bool = True,
) -> None:
    """Configure structlog for JSON output to console."""
    shared: list = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    if json_console:
        shared.append(structlog.processors.JSONRenderer())
    else:
        shared.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=shared + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: Optional[str] = None):  # type: ignore
    """Return a structlog logger bound with optional name."""
    return structlog.get_logger(name)
