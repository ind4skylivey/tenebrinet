# tenebrinet/core/logger.py (Final Final Attempt for this issue, focusing on ProcessorFormatter's __init__)
import logging
import structlog
import sys
import os
from logging.handlers import RotatingFileHandler
from structlog.stdlib import ProcessorFormatter # Explicitly import ProcessorFormatter

def configure_logger(
    log_level: str = "INFO",
    log_format: str = "json",
    log_output_path: str = "data/logs/tenebrinet.log",
    log_rotation_mb: int = 100
):
    """
    Configures the structlog-based logger for the TenebriNET application.

    Args:
        log_level: The minimum logging level to output (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
        log_format: The format of the log output ("json" or "console").
        log_output_path: The file path for log output.
        log_rotation_mb: The maximum size of the log file before rotation, in MB.
    """
    # Clear existing handlers from root logger to prevent duplicates during re-configuration in tests
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Processors for structlog.configure - these enrich the event dict.
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.PROCESS,
                    structlog.processors.CallsiteParameter.THREAD,
                    structlog.processors.CallsiteParameter.THREAD_NAME,
                }
            ),
            # This hands off the event dict to the standard logging system.
            # The dict is put into record.msg
            ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Processors that ProcessorFormatter will use to render the event dict (which is in record.msg)
    final_rendering_processors = [
        structlog.processors.JSONRenderer() if log_format == "json" else structlog.dev.ConsoleRenderer()
    ]

    # Configure the standard Python logging for routing structlog events.
    # ProcessorFormatter *is* a logging.Formatter, so fmt goes directly to it.
    # The 'processors' kwarg is for the structlog processors it will run.
    formatter = ProcessorFormatter(
        fmt="%(message)s", # Pass fmt directly to ProcessorFormatter
        processors=final_rendering_processors
    )

    # Ensure log directory exists
    log_dir = os.path.dirname(log_output_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_output_path,
        maxBytes=log_rotation_mb * 1024 * 1024, # Convert MB to Bytes
        backupCount=5, # Keep 5 backup logs
        encoding='utf8'
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level.upper())

    # Suppress noise from libraries
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("asyncio").propagate = False
    logging.getLogger("sqlalchemy").propagate = False
