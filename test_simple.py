#!/usr/bin/env python3
"""
Simple test to identify and fix errors in the Voice AI application.
"""
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test all module imports."""
    print("Testing imports...")
    
    try:
        from config import OPENAI_API_KEY, ELEVENLABS_API_KEY
        print("✓ Config module imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from audio_utils import AudioPlayer, HUMAN_TRAITS
        print("✓ Audio utils imported successfully")
    except Exception as e:
        print(f"✗ Audio utils import failed: {e}")
        return False
    
    try:
        from ai_brain import get_random_emotion
        print("✓ AI brain imported successfully")
    except Exception as e:
        print(f"✗ AI brain import failed: {e}")
        return False
    
    try:
        from utils.error_handler import setup_logging
        print("✓ Error handler imported successfully")
    except Exception as e:
        print(f"✗ Error handler import failed: {e}")
        return False
    
    return True

def test_emotion_function():
    """Test the get_random_emotion function."""
    print("\nTesting emotion function...")
    
    try:
        from ai_brain import get_random_emotion
        
        # Test different emotion types
        emotions = ['neutral', 'happy', 'sad', 'angry', 'invalid']
        for emotion in emotions:
            try:
                result = get_random_emotion(emotion)
                print(f"✓ get_random_emotion('{emotion}') = '{result}'")
            except Exception as e:
                print(f"✗ get_random_emotion('{emotion}') failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Emotion function test failed: {e}")
        return False

def test_audio_player():
    """Test the audio player initialization."""
    print("\nTesting audio player...")
    
    try:
        from audio_utils import AudioPlayer
        
        player = AudioPlayer()
        print("✓ AudioPlayer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ AudioPlayer initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Edward Voice AI - Error Detection Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_emotion_function,
        test_audio_player
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
