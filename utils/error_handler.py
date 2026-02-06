"""Error handling utilities for Edward Voice AI."""
import logging
import sys
import traceback
from typing import Callable, TypeVar, Any, Optional, Type, Tuple
from functools import wraps

# Type variable for generic function typing
T = TypeVar('T')

class VoiceAIError(Exception):
    """Base exception class for all Voice AI related errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AudioError(VoiceAIError):
    """Raised when there's an error with audio processing."""
    pass

class APIConnectionError(VoiceAIError):
    """Raised when there's an error connecting to an external API."""
    pass

class ConfigurationError(VoiceAIError):
    """Raised when there's a configuration error."""
    pass

def handle_error(
    exception_type: Type[Exception] = Exception,
    message: Optional[str] = None,
    status_code: int = 500,
    log_error: bool = True,
    reraise: bool = True
) -> Callable:
    """
    A decorator to handle exceptions in a consistent way.
    
    Args:
        exception_type: The type of exception to catch
        message: Custom error message (defaults to exception message)
        status_code: HTTP status code to associate with the error
        log_error: Whether to log the error
        reraise: Whether to re-raise the exception after handling
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                error_msg = message or str(e)
                error_details = {
                    'function': func.__name__,
                    'error_type': e.__class__.__name__,
                    'message': error_msg,
                    'status_code': getattr(e, 'status_code', status_code)
                }
                
                if log_error:
                    logging.error(
                        "Error in %s: %s",
                        func.__name__,
                        error_msg,
                        exc_info=True
                    )
                
                if reraise:
                    raise VoiceAIError(
                        message=error_msg,
                        status_code=error_details['status_code'],
                        details=error_details
                    ) from e
                return None
        return wrapper
    return decorator

def log_exception(logger: logging.Logger) -> Callable:
    """Decorator to log exceptions with traceback."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

def handle_gui_error(parent_window=None) -> Callable:
    """
    Decorator to handle errors in GUI functions and show user-friendly messages.
    
    Args:
        parent_window: The parent window for error dialogs
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except VoiceAIError as e:
                show_error_dialog(e, parent_window)
            except Exception as e:
                error = VoiceAIError(
                    "An unexpected error occurred",
                    status_code=500,
                    details={
                        'error': str(e),
                        'type': type(e).__name__
                    }
                )
                show_error_dialog(error, parent_window)
            return None
        return wrapper
    return decorator

def show_error_dialog(error: Exception, parent_window=None) -> None:
    """Show an error dialog with the error message."""
    import tkinter as tk
    from tkinter import messagebox
    
    if not isinstance(error, VoiceAIError):
        error = VoiceAIError(
            str(error),
            status_code=getattr(error, 'status_code', 500)
        )
    
    # Log the error
    logging.error(
        "Error [%d]: %s\nDetails: %s",
        error.status_code,
        error.message,
        error.details,
        exc_info=True
    )
    
    # Show error dialog
    if parent_window and hasattr(parent_window, 'tk'):
        try:
            messagebox.showerror(
                "Error",
                f"{error.message}\n\nError code: {error.status_code}",
                parent=parent_window
            )
        except Exception as e:
            logging.error("Failed to show error dialog: %s", str(e))
    else:
        print(f"Error [{error.status_code}]: {error.message}")
        if error.details:
            print("Details:", error.details)

def setup_logging(log_file: str = 'edward_ai.log') -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
