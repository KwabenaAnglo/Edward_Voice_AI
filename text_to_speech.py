"""
Text-to-speech module for Edward Voice AI.
Handles both pre-recorded voice responses and dynamic TTS via ElevenLabs.
"""
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class TTSConversionError(Exception):
    """Exception raised for errors in the TTS conversion process."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

# Import local modules
from config import AUDIO_DIR, VOICE_NAME, ELEVENLABS_API_KEY, ConfigError
from voice_manager import voice_manager, speak as _speak
from voice_responses import voice_responses
from audio_utils import play_response, audio_player

# Configure logging
logger = logging.getLogger(__name__)

# Configure ElevenLabs API key if available
ELEVENLABS_ENABLED = False
try:
    import elevenlabs
    
    if ELEVENLABS_API_KEY:
        try:
            # Try the newer API first
            from elevenlabs import ElevenLabs
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            # Test the API key by making a simple request
            voices = client.voices.get_all()
            ELEVENLABS_ENABLED = True
            logger.info("ElevenLabs TTS is enabled and API key is valid")
        except ImportError:
            # Fall back to older API
            try:
                from elevenlabs import set_api_key
                set_api_key(ELEVENLABS_API_KEY)
                voices = elevenlabs.voices()
                ELEVENLABS_ENABLED = True
                logger.info("ElevenLabs TTS is enabled and API key is valid (legacy API)")
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs with legacy API: {str(e)}")
                ELEVENLABS_ENABLED = False
                logger.warning("Dynamic TTS will be disabled due to invalid API key")
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {str(e)}")
            ELEVENLABS_ENABLED = False
            logger.warning("Dynamic TTS will be disabled due to invalid API key")
    else:
        logger.warning("ElevenLabs API key not found. Dynamic TTS will be disabled.")
        
except ImportError as e:
    logger.warning(f"ElevenLabs package not installed or import failed: {str(e)}. Dynamic TTS will be disabled.")
    ELEVENLABS_ENABLED = False

def speak(text: str, voice_name: str = None, emotion: str = 'neutral', 
         save_to_file: bool = False, use_tts_fallback: bool = True) -> bool:
    """
    Speak text using pre-recorded responses or TTS fallback.
    
    Args:
        text: The text to speak
        voice_name: Optional voice name (default: from config)
        emotion: Emotion for voice tone ('neutral', 'happy', 'sad', etc.)
        save_to_file: If True, save the TTS audio to a file
        use_tts_fallback: If True, use TTS when no pre-recorded response is found
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First try to find a matching pre-recorded response
        response = voice_responses.find_matching_response(text)
        
        # If no match but we have an emotion, try to get an emotion-based response
        if not response and emotion != 'neutral':
            response = voice_responses.get_emotion_response(emotion)
        
        # If we found a matching response, play it
        if response:
            return play_response(response)
            
        # If no matching response and TTS fallback is disabled, return False
        if not use_tts_fallback:
            logger.debug("No matching pre-recorded response found and TTS fallback is disabled")
            return False
            
        # Otherwise, use TTS as fallback
        logger.debug(f"No matching pre-recorded response found. Using TTS for: {text}")
        return _tts_speak(text, voice_name, save_to_file)
        
    except Exception as e:
        logger.error(f"Error in speak(): {e}", exc_info=True)
        return False

def _tts_speak(text: str, voice_name: str = None, save_to_file: bool = False) -> bool:
    """
    Internal function to handle TTS using ElevenLabs.
    """
    if not ELEVENLABS_ENABLED:
        logger.warning("TTS is not available. ElevenLabs is not properly configured.")
        return False
        
    try:
        save_path = os.path.join(AUDIO_DIR, f"tts_{int(time.time())}.mp3") if save_to_file else None
        voice_name = voice_name or VOICE_NAME
        
        # Use the voice manager to handle the TTS
        audio_data = _speak(text, voice_name=voice_name, save_path=save_path)
        return audio_data is not None
        
    except Exception as e:
        logger.error(f"Error in TTS: {e}", exc_info=True)
        return False
    return _speak(text, voice_name=voice_name, save_path=save_path)

def list_available_voices() -> list:
    """
    Get a list of available voice names.
    
    Returns:
        list: List of available voice names
    """
    return voice_manager.list_available_voices()

def clone_voice(name: str, description: str, audio_files: list) -> bool:
    """
    Create a custom voice clone.
    
    Args:
        name: Name for the new voice
        description: Description of the voice
        audio_files: List of paths to audio files (1-25) for cloning
        
    Returns:
        bool: True if successful, False otherwise
    """
    return voice_manager.clone_voice(name, description, audio_files)

def set_voice_settings(**kwargs) -> None:
    """
    Update voice synthesis settings.
    
    Args:
        **kwargs: Voice settings to update (stability, similarity_boost, etc.)
    """
    voice_manager.set_voice_settings(**kwargs)
