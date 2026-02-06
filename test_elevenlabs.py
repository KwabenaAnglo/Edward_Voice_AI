import sys
import os
from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY

# Set console output to support UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_elevenlabs():
    print("Testing ElevenLabs API Connection...")
    print("-" * 40)
    
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == 'your_elevenlabs_api_key_here':
        print("[ERROR] Please update your ElevenLabs API key in the .env file")
        return
    
    try:
        # Initialize the client
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Test getting voices
        print("\n[INFO] Fetching available voices...")
        voices = client.voices.get_all()
        
        print(f"\n[SUCCESS] Connected to ElevenLabs API!")
        print(f"[INFO] Found {len(voices.voices)} voices")
        print("\nAvailable voices:")
        for i, voice in enumerate(voices.voices[:5], 1):  # Show first 5 voices
            print(f"{i}. {voice.name} ({voice.category})")
        if len(voices.voices) > 5:
            print(f"... and {len(voices.voices) - 5} more voices")
            
    except Exception as e:
        print(f"[ERROR] Connecting to ElevenLabs: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure your API key is correct and active")
        print("2. Check your internet connection")
        print("3. Ensure you have a valid subscription on ElevenLabs")
        print("4. Visit https://elevenlabs.io/api for more help")
        print(f"\nCurrent API key (first 10 chars): {ELEVENLABS_API_KEY[:10]}...")

if __name__ == "__main__":
    test_elevenlabs()
