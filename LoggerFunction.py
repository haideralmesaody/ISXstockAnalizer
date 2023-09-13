import logging
from logging.handlers import RotatingFileHandler
import uuid
from app_config import DEBUG  # Import your DEBUG flag from your config

class Logger:
    _instance = None

    def __new__(cls, debug: bool = DEBUG):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.debug = debug

            log_format = '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'

            # Handler for regular logs
            handler = RotatingFileHandler('stock_analysis.log', maxBytes=1e6, backupCount=5)
            handler.setFormatter(logging.Formatter(log_format))

            # Handler for full logs of truncated messages
            full_handler = RotatingFileHandler('stock_analysis_full.log', maxBytes=1e6, backupCount=5)
            full_handler.setFormatter(logging.Formatter(log_format))

            logger = logging.getLogger('main_logger')
            logger.propagate = False
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG if cls._instance.debug else logging.INFO)

            cls._instance.full_logger = logging.getLogger('full_logger')
            cls._instance.full_logger.addHandler(full_handler)
            cls._instance.full_logger.setLevel(logging.DEBUG if cls._instance.debug else logging.INFO)

        return cls._instance

    def log_or_print(self, msg: str, level: str = "INFO", exc_info: bool = False, module: str = None):
        try:
            logger = logging.getLogger('main_logger')
            log_method = getattr(logger, level.lower(), None)

            if log_method is None:
                msg = f"Unsupported log level: {level}"
                logger.error(msg)
                raise ValueError(msg)

            # Generate a unique ID for this log entry
            log_id = str(uuid.uuid4())

            # Get the log level value
            log_level_value = logging.getLevelName(level.upper())

            if len(msg) > 1000:
                truncated_msg = msg[:1000] + '...'  # Truncate the message
                self.full_logger.log(log_level_value, f"{log_id} - {msg}")  # Log the full message in the second log file
            else:
                truncated_msg = msg

            if module:
                truncated_msg = f"{module} - {truncated_msg}"

            log_method(f"{log_id} - {truncated_msg}", exc_info=exc_info)

            if self.debug:
                print(f"{level.upper()} - {truncated_msg}")

        except Exception as e:
            # Handle unexpected errors gracefully
            error_msg = f"Error occurred in log_or_print: {e}"
            logger.error(error_msg)
            if self.debug:
                print(f"ERROR - {error_msg}")

if __name__ == "__main__":
    logger = Logger(debug=True)
    logger.log_or_print("This is a very long message, designed primarily to test whether the log message truncation feature is working as expected.", level="DEBUG", module="TestModule")
