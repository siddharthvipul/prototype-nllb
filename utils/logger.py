import logging
from logging.handlers import RotatingFileHandler
from threading import Lock

class Logger:
    _instance = None
    _lock = Lock()  # Ensures thread-safe singleton access

    def __new__(self, log_level=logging.INFO, log_file=None, name="Logger"):
        with self._lock:
            if self._instance is None:
                self._instance = super().__new__(self)
                self._instance._initialize(log_level, log_file, name)
            return self._instance

    def _initialize(self, log_level, log_file, name):
        """Initializes the logger with dynamic log level and optional file output."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Avoid adding multiple handlers if logger is reinitialized
        if not self.logger.hasHandlers():
            # Stream handler for console output
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(stream_handler)

            if log_file:
                # Rotating file handler to manage log files efficiently
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=5 * 1024 * 1024, backupCount=5
                )
                file_handler.setFormatter(self._get_formatter())
                self.logger.addHandler(file_handler)

    def _get_formatter(self):
        """Defines a standard format for log messages."""
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    @staticmethod
    def get_logger():
        """Returns the singleton logger instance."""
        if Logger._instance is None:
            raise Exception("Logger is not initialized. Call Logger() first.")
        return Logger._instance.logger

    def set_level(self, log_level):
        """Allows dynamic change of logging level at runtime."""
        self.logger.setLevel(log_level)