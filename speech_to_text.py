import openai
import os
from typing import Optional
from config import OPENAI_API_KEY, ConfigError

class SpeechRecognitionError(Exception):
    """Custom exception for speech recognition errors."""
    pass

def speech_to_text(audio_file: str) -> str:
    """
    Convert speech from an audio file to text using OpenAI's Whisper API.
    
    Args:
        audio_file: Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text
        
    Raises:
        SpeechRecognitionError: If there's an error during speech recognition
        FileNotFoundError: If the audio file doesn't exist
        PermissionError: If there's no permission to read the audio file
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    
    if not os.access(audio_file, os.R_OK):
        raise PermissionError(f"No permission to read audio file: {audio_file}")
    
    if not OPENAI_API_KEY:
        raise ConfigError("OpenAI API key is not configured")
    
    try:
        with open(audio_file, "rb") as file:
            transcript = openai.audio.transcriptions.create(
                file=file,
                model="whisper-1"
            )
        return transcript.text
        
    except openai.OpenAIError as e:
        raise SpeechRecognitionError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise SpeechRecognitionError(f"Error in speech recognition: {str(e)}")
