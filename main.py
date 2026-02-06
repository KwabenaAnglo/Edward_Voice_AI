"""
Edward Voice AI - Main Application

This module serves as the entry point for the Edward Voice AI application.
It initializes the application and handles top-level exceptions.
"""
import sys
import logging
from utils.error_handler import setup_logging

# Set up logging
setup_logging('edward_ai.log')
logger = logging.getLogger(__name__)

def main() -> int:
    """Main entry point for the application."""
    try:
        # Import here to avoid circular imports
        import gui
        return gui.main()
    except ImportError as e:
        logger.critical("Failed to import required modules: %s", str(e), exc_info=True)
        print(f"Error: Failed to import required modules: {e}")
        return 1
    except Exception as e:
        logger.critical("Fatal error: %s", str(e), exc_info=True)
        print(f"A fatal error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
