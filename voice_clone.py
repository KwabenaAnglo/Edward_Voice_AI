"""
Voice Cloning Script for Edward Voice AI

This script clones Edward's voice using ElevenLabs API.
"""
import os
import logging
from typing import List, Optional
from elevenlabs import ElevenLabs, Voice
from config import ELEVENLABS_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloner:
    def __init__(self):
        """Initialize the voice cloner with ElevenLabs client."""
        if not ELEVENLABS_API_KEY:
            raise ValueError("ElevenLabs API key not found in config")
        
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.voice_files = [
            "Warm_up.m4a.mp4",
            "Basic_intro.m4a.mp4", 
            "Everyday_conversation style.m4a.mp4",
            "Explaining_something.m4a.mp4",
            "Opinion_emphasis.m4a.mp4",
            "Tone_shift.m4a.mp4",
            "Free_talk.m4a.mp4"
        ]
    
    def check_files_exist(self) -> bool:
        """Check if all voice files exist in the project folder."""
        missing_files = []
        for file in self.voice_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"Missing voice files: {missing_files}")
            return False
        
        logger.info("All voice files found ✓")
        return True
    
    def clone_voice(self, voice_name: str = "Edward") -> Optional[Voice]:
        """
        Clone Edward's voice using the provided audio files.
        
        Args:
            voice_name: Name for the cloned voice
            
        Returns:
            Voice object if successful, None otherwise
        """
        try:
            logger.info(f"Starting voice cloning for '{voice_name}'...")
            
            # Check if files exist
            if not self.check_files_exist():
                return None
            
            # Create voice clone using the correct API
            logger.info("Creating voice clone...")
            from elevenlabs import clone
            voice = clone(
                api_key=ELEVENLABS_API_KEY,
                name=voice_name,
                files=self.voice_files,
                description="Edward's natural speaking voice - casual, confident, and conversational"
            )
            
            logger.info(f"✅ Voice '{voice_name}' cloned successfully!")
            logger.info(f"Voice ID: {voice.voice_id}")
            
            return voice
            
        except Exception as e:
            logger.error(f"❌ Failed to clone voice: {str(e)}")
            return None
    
    def test_voice(self, voice_id: str, test_text: str = "Hey, what's up? Just testing out my new voice clone. Sounds pretty natural, right?") -> bool:
        """
        Test the cloned voice with a sample text.
        
        Args:
            voice_id: ID of the cloned voice
            test_text: Text to speak for testing
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            logger.info("Testing cloned voice...")
            
            # Generate audio using the correct API
            from elevenlabs import generate
            audio = generate(
                api_key=ELEVENLABS_API_KEY,
                text=test_text,
                voice=Voice(voice_id=voice_id)
            )
            
            # Save test audio
            test_file = "test_cloned_voice.mp3"
            with open(test_file, "wb") as f:
                f.write(audio)
            
            logger.info(f"✅ Test audio saved as '{test_file}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to test voice: {str(e)}")
            return False
    
    def list_voices(self) -> List[Voice]:
        """List all available voices."""
        try:
            from elevenlabs import voices
            all_voices = voices(api_key=ELEVENLABS_API_KEY)
            logger.info("Available voices:")
            for voice in all_voices:
                logger.info(f"- {voice.name} (ID: {voice.voice_id})")
            return all_voices
        except Exception as e:
            logger.error(f"Failed to list voices: {str(e)}")
            return []

def main():
    """Main function to run the voice cloning process."""
    try:
        cloner = VoiceCloner()
        
        # List existing voices
        logger.info("=== Current Voices ===")
        cloner.list_voices()
        
        # Clone the voice
        logger.info("\n=== Starting Voice Clone ===")
        voice = cloner.clone_voice("Edward")
        
        if voice:
            # Test the cloned voice
            logger.info("\n=== Testing Cloned Voice ===")
            cloner.test_voice(voice.voice_id)
            
            logger.info("\n✅ Voice cloning complete!")
            logger.info(f"Use voice ID '{voice.voice_id}' in your config")
        else:
            logger.error("❌ Voice cloning failed")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
