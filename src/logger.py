"""Logging module for weekly reports generator."""
import logging
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """Logger class for capturing and writing logs."""

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        self.log_file = Path(log_dir) / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger('weekly_reports')
        logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        logger.handlers.clear()

        # File handler
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

    def log_start(self, message: str = "Starting Weekly Tech Reports Generator"):
        """Log start of execution."""
        self.info("=" * 50)
        self.info(message)
        self.info(f"Log file: {self.log_file}")
        self.info("=" * 50)

    def log_end(self, message: str = "Execution completed"):
        """Log end of execution."""
        self.info("=" * 50)
        self.info(message)
        self.info("=" * 50)

    def log_summary(self, summary: dict):
        """Log execution summary."""
        self.info("-" * 50)
        self.info("Execution Summary:")
        for key, value in summary.items():
            self.info(f"  {key}: {value}")
        self.info("-" * 50)
