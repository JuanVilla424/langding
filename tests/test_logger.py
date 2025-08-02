"""
Tests for the logging module.
"""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from src.logger import setup_logger, logger


class TestLogger:
    """Test cases for logging functionality."""

    def test_setup_logger_default(self):
        """Test logger setup with default parameters."""
        test_logger = setup_logger("test_logger")

        assert test_logger.name == "test_logger"
        assert test_logger.level == logging.INFO
        assert len(test_logger.handlers) >= 1  # At least console handler

    def test_setup_logger_with_file(self):
        """Test logger setup with file logging."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_logger = setup_logger("test_logger_file", log_file=temp_file.name)

            assert test_logger.name == "test_logger_file"
            assert len(test_logger.handlers) == 2  # Console + file handlers

    def test_setup_logger_debug_level(self):
        """Test logger setup with DEBUG level."""
        test_logger = setup_logger("test_debug", level=logging.DEBUG)

        assert test_logger.level == logging.DEBUG

    def test_logger_no_propagation(self):
        """Test that logger doesn't propagate to parent loggers."""
        test_logger = setup_logger("test_no_prop")

        assert test_logger.propagate is False

    def test_logger_handlers_not_duplicated(self):
        """Test that handlers are not duplicated on multiple calls."""
        logger_name = "test_no_duplicate"

        # Call setup_logger multiple times
        logger1 = setup_logger(logger_name)
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_logger(logger_name)
        final_handler_count = len(logger2.handlers)

        # Should not add duplicate handlers
        assert initial_handler_count == final_handler_count
        assert logger1 is logger2  # Same logger instance

    def test_logs_directory_creation(self):
        """Test that logs directory is created."""
        logs_dir = Path("logs")

        # Even if directory doesn't exist, setup_logger should create it
        setup_logger("test_dir_creation", log_file="logs/test.log")

        assert logs_dir.exists()
        assert logs_dir.is_dir()

    def test_global_logger_exists(self):
        """Test that global logger is available."""
        assert logger is not None
        assert logger.name == "app"

    def test_logger_message_formatting(self):
        """Test logger message formatting."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log") as temp_file:
            test_logger = setup_logger("test_format", log_file=temp_file.name)

            # Log a test message
            test_message = "Test log message"
            test_logger.info(test_message)

            # Read the log file
            temp_file.seek(0)
            log_content = temp_file.read()

            # Verify message format in file (should include timestamp, name, level)
            # Note: Console output only shows message, file output shows full format

    def test_logger_encoding(self):
        """Test logger handles UTF-8 encoding properly."""
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".log", encoding="utf-8"
        ) as temp_file:
            test_logger = setup_logger("test_encoding", log_file=temp_file.name)

            # Log message with unicode characters
            unicode_message = "Test with unicode: 🚀 español français 中文"
            test_logger.info(unicode_message)

            # Should not raise encoding errors

    @patch("src.logger.logging.FileHandler")
    @patch("src.logger.logging.StreamHandler")
    def test_handler_formatters(self, mock_stream_handler, mock_file_handler):
        """Test that proper formatters are applied to handlers."""
        mock_stream_instance = Mock()
        mock_file_instance = Mock()
        mock_stream_handler.return_value = mock_stream_instance
        mock_file_handler.return_value = mock_file_instance

        setup_logger("test_formatters", log_file="test.log")

        # Verify setFormatter was called on both handlers
        mock_stream_instance.setFormatter.assert_called_once()
        mock_file_instance.setFormatter.assert_called_once()

    def test_different_log_levels(self):
        """Test logging at different levels."""
        test_logger = setup_logger("test_levels", level=logging.DEBUG)

        # These should not raise exceptions
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        test_logger.critical("Critical message")

    def test_logger_integration_with_main(self):
        """Test that logger works properly when imported by main module."""
        from src.logger import logger as main_logger

        assert main_logger is not None
        assert isinstance(main_logger, logging.Logger)

        # Should be able to log without errors
        main_logger.info("Integration test message")
