import os
import json
import requests
import time
from pathlib import Path
from typing import Optional, Dict, List, Union
from elevenlabs import Voice, VoiceSettings, play, voices
from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY, AUDIO_DIR, VOICE_SETTINGS, VOICE_NAME

class VoiceManager:
    """Manages voice synthesis including custom voice cloning."""
    
    def __init__(self):
        """Initialize the voice manager with API key and settings."""
        self.voices = {}
        self.voice_settings = VoiceSettings(
            stability=0.7,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True
        )
        self.current_voice = VOICE_NAME
        self.api_key = ELEVENLABS_API_KEY
        
        # Initialize the ElevenLabs client only if API key is available
        self.client = None
        if self.api_key:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize ElevenLabs client: {e}")
        
        # Create audio directory if it doesn't exist
        os.makedirs(AUDIO_DIR, exist_ok=True)
        
        # Load available voices
        self.load_voices()
        
        # If no voices loaded, add fallback voices
        if not self.voices:
            self.add_fallback_voices()
        
    def load_voices(self) -> None:
        """Load available voices from ElevenLabs API."""
        if not self.client:
            print("ElevenLabs client not initialized - skipping voice loading")
            self.voices = {}
            return
            
        try:
            # Get voices using the client
            voices_list = self.client.voices.get_all()
            self.voices = {voice.name: voice for voice in voices_list.voices}
            print(f"Loaded {len(self.voices)} voices from ElevenLabs")
        except Exception as e:
            print(f"Error loading voices: {e}")
            self.voices = {}
    
    def add_fallback_voices(self) -> None:
        """Add fallback voices when ElevenLabs is not available."""
        print("Adding fallback voices for offline mode...")
        
        # Create mock voice objects for fallback
        class FallbackVoice:
            def __init__(self, name: str, voice_id: str):
                self.name = name
                self.voice_id = voice_id
        
        fallback_voices = [
            FallbackVoice("Adam", "fallback-adam"),
            FallbackVoice("Alice", "fallback-alice"), 
            FallbackVoice("Sam", "fallback-sam"),
            FallbackVoice("Default", "fallback-default")
        ]
        
        self.voices = {voice.name: voice for voice in fallback_voices}
        print(f"Added {len(self.voices)} fallback voices")
    
    def list_available_voices(self) -> List[str]:
        """Get a list of available voice names."""
        return list(self.voices.keys())
    
    def set_voice_settings(self, **kwargs) -> None:
        """Update voice synthesis settings."""
        for key, value in kwargs.items():
            if hasattr(self.voice_settings, key):
                setattr(self.voice_settings, key, value)
    
    def text_to_speech(
        self,
        text: str,
        voice_name: str = None,
        save_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            voice_name: Optional voice name (uses current voice if None)
            save_path: Optional path to save the audio file
            
        Returns:
            bytes: Audio data if successful, None otherwise
        """
        if not text.strip():
            return None

        voice_name = voice_name or self.current_voice
        if voice_name not in self.voices:
            print(f"Voice '{voice_name}' not found. Using default voice.")
            voice_name = next(iter(self.voices.keys()), None)
            if not voice_name:
                print("No voices available.")
                return None

        # Get the voice object by name
        voice = self.voices.get(voice_name)
        if not voice:
            print(f"Voice '{voice_name}' not found")
            return None
        
        # Check if this is a fallback voice
        if hasattr(voice, 'voice_id') and voice.voice_id.startswith('fallback-'):
            print(f"Using fallback voice '{voice_name}' - ElevenLabs TTS not available")
            print("Note: To enable actual voice synthesis, please add a valid ElevenLabs API key")
            # Try to use system TTS as fallback
            return self.fallback_tts(text, save_path)

        # Try to generate speech using ElevenLabs
        if not self.client:
            print("ElevenLabs client not available - trying fallback TTS")
            return self.fallback_tts(text, save_path)
            
        try:
            # Generate speech using the client
            audio = self.client.generate(
                text=text,
                voice=voice,
                model="eleven_monolingual_v2",
                voice_settings=self.voice_settings
            )
            
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(audio)
            
            return audio
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def fallback_tts(self, text: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """
        Fallback TTS using system speech synthesis when ElevenLabs is not available.
        
        Args:
            text: Text to convert to speech
            save_path: Optional path to save the audio file
            
        Returns:
            bytes: Audio data if successful, None otherwise
        """
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Convert speech to bytes using a temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            try:
                # Save speech to temporary file
                engine.save_to_file(text, temp_path)
                engine.runAndWait()
                
                # Read the audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Save to requested path if specified
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(audio_data)
                
                print("✓ Generated speech using system TTS")
                return audio_data
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except ImportError:
            print("System TTS not available (pyttsx3 not installed)")
            print("To install: pip install pyttsx3")
            return None
        except Exception as e:
            print(f"Fallback TTS failed: {e}")
            return None
    
    def play_audio(self, audio_data: bytes) -> None:
        """Play audio data."""
        try:
            if audio_data:
                # Try ElevenLabs play function first
                try:
                    play(audio_data)
                except:
                    # Fallback to playing with pyaudio
                    import pyaudio
                    import wave
                    import tempfile
                    import os
                    
                    # Save to temporary file and play with pyaudio
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        tmp_file.write(audio_data)
                        temp_path = tmp_file.name
                    
                    try:
                        # Play using wave and pyaudio
                        with wave.open(temp_path, 'rb') as wf:
                            p = pyaudio.PyAudio()
                            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                         channels=wf.getnchannels(),
                                         rate=wf.getframerate(),
                                         output=True)
                            
                            data = wf.readframes(1024)
                            while data:
                                stream.write(data)
                                data = wf.readframes(1024)
                            
                            stream.stop_stream()
                            stream.close()
                            p.terminate()
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def clone_voice(self, name: str, description: str, audio_files: List[str]) -> bool:
        """
        Create a custom voice clone.
        
        Args:
            name: Name for the new voice
            description: Description of the voice
            audio_files: List of paths to audio files (1-25) for cloning
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not all(os.path.exists(f) for f in audio_files):
            print("Error: One or more audio files not found")
            return False
            
        try:
            # Create the voice clone
            voice = Voice.from_local_audio_pack(
                voice_name=name,
                description=description,
                files=audio_files
            )
            
            # Update the voices list
            self.load_voices()
            return True
            
        except Exception as e:
            print(f"Error cloning voice: {e}")
            return False

# Initialize voice manager
voice_manager = VoiceManager()

def speak(text: str, voice_name: str = None, save_path: str = None) -> Optional[bytes]:
    """
    Simple interface for text-to-speech.
    
    Args:
        text: Text to speak
        voice_name: Optional voice name (default: from config)
        save_path: Optional path to save the audio file
    """
    return voice_manager.text_to_speech(text, voice_name, save_path)
