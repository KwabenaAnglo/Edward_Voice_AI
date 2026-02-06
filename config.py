import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def load_environment() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        logger.warning("No .env file found. Using system environment variables.")
    try:
        load_dotenv(env_path)
    except Exception as e:
        logger.warning(f"Failed to load .env file: {e}. Using system environment variables.")

def validate_required_vars() -> None:
    """Validate that all required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ConfigError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Load environment variables
load_environment()

# API Keys
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

# Application Settings
ASSISTANT_NAME: str = os.getenv("ASSISTANT_NAME", "Edward")
VOICE_NAME: str = os.getenv("VOICE_NAME", "Adam")
DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en-US")

# File Paths
BASE_DIR: Path = Path(__file__).parent.absolute()
DATA_DIR: Path = BASE_DIR / "data"
AUDIO_DIR: Path = DATA_DIR / "audio"
MODELS_DIR: Path = DATA_DIR / "models"

# Create necessary directories
try:
    for directory in [DATA_DIR, AUDIO_DIR, MODELS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
except OSError as e:
    logger.error(f"Failed to create required directories: {e}")
    raise

# Conversation Settings
CONVERSATION_HISTORY_FILE: Path = DATA_DIR / "conversation_history.json"
MAX_CONVERSATION_HISTORY: int = 15  # Number of exchanges to keep in memory

# Validate configuration
if __name__ == "__main__":
    try:
        validate_required_vars()
        logger.info("Configuration is valid")
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        raise

# Voice Settings
VOICE_SETTINGS = {
    "rate": 1.0,  # Speech rate (0.5 to 2.0)
    "volume": 1.0,  # Volume (0.0 to 1.0)
    "pitch": 1.0,   # Pitch adjustment
}

# Offline Mode Settings
OFFLINE_MODE = False  # Set to True to enable offline capabilities
OFFLINE_MODEL_PATH = MODELS_DIR / "offline_model"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = DATA_DIR / "edward_ai.log"

# Initialize OpenAI client
import openai
openai.api_key = OPENAI_API_KEY
