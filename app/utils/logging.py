import logging
import sys

def get_logger() -> logging.Logger:
    """
    Create or retrieve a configured logger instance.

    This utility ensures consistent logging configuration across the application.
    Outputs to stdout and formats logs with timestamps and log levels.

    Returns:
        logging.Logger: A configured logger instance ready for use.
    """
    logger = logging.getLogger()
    
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
