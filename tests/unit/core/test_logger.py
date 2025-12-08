# tests/unit/core/test_logger.py
import pytest
import structlog
import logging
import os
import json
from unittest.mock import patch, MagicMock
from logging.handlers import RotatingFileHandler
import sys

# Import the configure_logger function
from tenebrinet.core.logger import configure_logger


# Fixture to temporarily set up and tear down the logger configuration
@pytest.fixture
def configured_logger(tmp_path):
    log_file = tmp_path / "test.log"
    configure_logger(
        log_level="DEBUG",
        log_format="json",
        log_output_path=str(log_file),
        log_rotation_mb=1
    )
    yield structlog.get_logger("test_logger")
    # Teardown: remove handlers to avoid interference with other tests
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


def test_logger_initialization_and_level(configured_logger):
    """Test that the logger is correctly initialized and respects log level."""
    assert configured_logger.isEnabledFor(logging.DEBUG)
    assert not configured_logger.isEnabledFor(logging.NOTSET)


def test_json_formatting(configured_logger, tmp_path):
    """Test that logs are formatted as JSON in the output file."""
    log_file = tmp_path / "test.log"
    configured_logger.info("Test message", key="value", number=123)

    # Need to ensure the log is actually written before reading
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.flush()

    with open(log_file, 'r') as f:
        log_entry = json.loads(f.readline())
        assert log_entry["event"] == "Test message"
        assert log_entry["key"] == "value"
        assert log_entry["number"] == 123
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "logger" in log_entry
        assert log_entry["logger"] == "test_logger"


def test_log_rotation(configured_logger, tmp_path):
    """Test that log rotation works as expected."""
    log_file = tmp_path / "test.log"

    # We will write a specific pattern to identify it in the rotated file
    unique_message_part = "--- ROTATION TEST MESSAGE ---"

    # Write messages until rotation is guaranteed to have happened
    for i in range(10000):
        # Writing a message with enough content
        log_data = {
            "event": f"Log line {i}: {unique_message_part}",
            "data_index": i,
            "padding": "a" * 100
        }
        configured_logger.info(**log_data)

        # Manually flush to ensure disk writes happen and size is updated
        for handler in logging.getLogger().handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.flush()

        # Check if the rotated file already exists
        if os.path.exists(str(log_file) + ".1"):
            break

    # Force a final flush and rollover check if not already done
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.flush()
            handler.doRollover()

    # After writing, ensure the rotation has occurred.
    assert os.path.exists(log_file)
    assert os.path.exists(str(log_file) + ".1")

    # Verify content of the rotated file (log_file.1)
    with open(str(log_file) + ".1", 'r') as f:
        rotated_content = f.read()
        assert unique_message_part in rotated_content
        assert rotated_content.strip().startswith("{")

    # Verify the current log_file is now small
    with open(log_file, 'r') as f:
        current_content = f.read()
        assert unique_message_part not in current_content

    assert os.path.getsize(log_file) < 1000


def test_console_output(tmp_path):
    """Test that console output works when format is 'console'."""
    log_file = tmp_path / "console_test.log"
    root_logger_console = logging.getLogger()
    for handler in root_logger_console.handlers[:]:
        root_logger_console.removeHandler(handler)

    with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
        configure_logger(
            log_level="INFO",
            log_format="console",
            log_output_path=str(log_file),
            log_rotation_mb=1
        )
        logger_console = structlog.get_logger("console_logger")
        logger_console.info("Console message", data="xyz")

        for handler in logging.getLogger().handlers:
            is_stream = isinstance(handler, logging.StreamHandler)
            if is_stream and handler.stream == sys.stdout:
                handler.flush()

        assert mock_stdout.write.call_count > 0
        captured_output = mock_stdout.write.call_args[0][0]

        # Assert the presence of the main message
        assert "Console message" in captured_output

        # Assert the presence of the key and value separately
        assert "data" in captured_output
        assert "xyz" in captured_output

        # Assert the log level is present
        assert "info" in captured_output

        # Optionally, check for ANSI escape codes
        assert "\x1b" in captured_output

    root_logger_console = logging.getLogger()
    for handler in root_logger_console.handlers[:]:
        root_logger_console.removeHandler(handler)
