"""
Audio utilities for Edward Voice AI.
Handles audio playback and related functionality.
"""
import os
import wave
import pyaudio
import time
from typing import Optional
from pathlib import Path

class AudioPlayer:
    """Handles audio playback functionality."""
    
    def __init__(self):
        """Initialize the audio player."""
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        
    def play_audio_file(self, file_path: str, block: bool = True) -> bool:
        """
        Play an audio file.
        
        Args:
            file_path: Path to the audio file
            block: If True, blocks until playback is complete
            
        Returns:
            bool: True if playback was successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            return False
            
        try:
            with wave.open(file_path, 'rb') as wf:
                def callback(in_data, frame_count, time_info, status):
                    data = wf.readframes(frame_count)
                    return (data, pyaudio.paContinue)
                
                self.stream = self.pyaudio.open(
                    format=self.pyaudio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback
                )
                
                self.is_playing = True
                
                if block:
                    while self.stream.is_active():
                        time.sleep(0.1)
                    self.stop()
                    
                return True
                
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def stop(self):
        """Stop any currently playing audio."""
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.is_playing = False
    
    def __del__(self):
        """Clean up resources."""
        self.stop()
        if hasattr(self, 'pyaudio'):
            self.pyaudio.terminate()

# Global instance for easy importing
audio_player = AudioPlayer()

HUMAN_TRAITS = {"EMOTIONS":["angry","disust","fear","joy","sadness","surprise","neutral"]        
    }
def play_response(response: dict) -> bool:
    """
    Play a voice response.
    
    Args:
        response: A response dictionary with 'file' and 'text' keys
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    if not response or 'file' not in response:
        return False
    
    print(f"Playing: {response.get('text', '')}")
    return audio_player.play_audio_file(response['file'])

def speak_text(text: str, emotion: str = 'neutral') -> bool:
    """
    Speak the given text with the specified emotion.
    
    Args:
        text: The text to speak
        emotion: The emotion to use (affects voice tone)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # First try to find a matching pre-recorded response
    from voice_responses import voice_responses
    
    # Look for an exact match in the responses
    response = voice_responses.find_matching_response(text)
    
    # If no exact match, try to get a response based on emotion
    if not response and emotion != 'neutral':
        response = voice_responses.get_emotion_response(emotion)
    
    # If we found a matching response, play it
    if response:
        return play_response(response)
    
    # Otherwise, use TTS (to be implemented)
    print(f"[TTS] {text}")
    return False
