# import logging
#
#
# def get_logger(name: str = __name__):
#     logger = logging.getLogger(name)
#     logging.basicConfig(level=logging.INFO)
import logging
import sys
from pathlib import Path

def get_logger(name: str = __name__):
    """
    Create and return a configured logger instance.
    This ensures consistent logging format across the backend.
    """
    logger = logging.getLogger(name)

    # Avoid re-adding handlers if logger already exists
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # File handler (optional: stores logs in backend/logs/app.log)
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.INFO)

        # Common log format
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Prevent duplicate logs
        logger.propagate = False

    return logger
