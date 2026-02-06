import logging
from pathlib import Path
from datetime import datetime
from config import config

def setup_logger(name):
    """
    Configure and return a logger with both file and console handlers.
    
    Args:
        name (str): Name of the logger (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Create file handler which logs debug messages
    log_file = config.LOGS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    if not logger.handlers:  # Avoid adding handlers multiple times
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
