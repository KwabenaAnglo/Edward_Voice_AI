"""
Test script to verify ElevenLabs API key and connection.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

if not ELEVENLABS_API_KEY:
    print("❌ Error: ELEVENLABS_API_KEY not found in environment variables")
    print("Please add it to your .env file or set it as an environment variable")
    sys.exit(1)

print(f"🔑 Found ElevenLabs API key: {ELEVENLABS_API_KEY[:5]}...{ELEVENLABS_API_KEY[-5:]}")

# Try to import and test the API
try:
    from elevenlabs.client import ElevenLabs
    
    print("\n🔌 Testing ElevenLabs API connection...")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    # Test API key by making a simple request
    voices = client.voices.get_all()
    print(f"✅ Success! Found {len(voices.voices)} available voices")
    
    # Print first 3 voices as a sample
    print("\nSample of available voices:")
    for voice in voices.voices[:3]:
        print(f"- {voice.name} (ID: {voice.voice_id})")
    
    print("\n🎉 Your ElevenLabs API key is working correctly!")
    
except ImportError:
    print("\n❌ Error: elevenlabs package not installed.")
    print("Please install it with: pip install elevenlabs")
    
except Exception as e:
    print(f"\n❌ Error testing ElevenLabs API: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Verify your API key is correct")
    print("2. Check your internet connection")
    print("3. Make sure your account has sufficient credits")
    print("4. Check the ElevenLabs status page: https://status.elevenlabs.io/")
    sys.exit(1)
