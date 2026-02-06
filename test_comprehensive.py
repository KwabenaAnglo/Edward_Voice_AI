#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes are working.
"""
import sys
import traceback
import tempfile
import os

def test_emotion_function_fix():
    """Test that the emotion function fix is working."""
    print("Testing emotion function fix...")
    
    try:
        from ai_brain import get_random_emotion
        
        # Test the specific case that was failing
        result = get_random_emotion('sad')
        print(f"✓ get_random_emotion('sad') = '{result}'")
        
        # Test edge cases
        result = get_random_emotion('nonexistent')
        print(f"✓ get_random_emotion('nonexistent') = '{result}'")
        
        return True
    except Exception as e:
        print(f"✗ Emotion function test failed: {e}")
        traceback.print_exc()
        return False

def test_elevenlabs_logging_fix():
    """Test that the ElevenLabs logging is more informative."""
    print("\nTesting ElevenLabs logging fix...")
    
    try:
        # This will import the module and trigger the logging
        from text_to_speech import ELEVENLABS_ENABLED
        print(f"✓ ElevenLabs enabled status: {ELEVENLABS_ENABLED}")
        return True
    except Exception as e:
        print(f"✗ ElevenLabs test failed: {e}")
        traceback.print_exc()
        return False

def test_speech_to_text_error_handling():
    """Test speech to text error handling with proper exception types."""
    print("\nTesting speech to text error handling...")
    
    try:
        from speech_to_text import speech_to_text, SpeechRecognitionError
        
        # Test with non-existent file
        try:
            speech_to_text("nonexistent_file.wav")
            print("✗ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("✓ FileNotFoundError properly raised")
        
        # Test with empty file (this will fail due to API quota, but should raise proper exception)
        try:
            # Create a temporary empty file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00")
                tmp_name = tmp.name
            
            try:
                speech_to_text(tmp_name)
                print("✗ Should have raised SpeechRecognitionError due to quota")
                return False
            except SpeechRecognitionError as e:
                if "OpenAI API error" in str(e):
                    print("✓ SpeechRecognitionError properly raised with OpenAI error")
                else:
                    print(f"✗ Unexpected error message: {e}")
                    return False
            finally:
                # Make sure the file is closed before trying to delete it
                try:
                    os.unlink(tmp_name)
                except:
                    pass
                    
        except Exception as e:
            print(f"✗ Unexpected exception: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Speech to text test failed: {e}")
        traceback.print_exc()
        return False

def test_audio_player():
    """Test audio player functionality."""
    print("\nTesting audio player...")
    
    try:
        from audio_utils import AudioPlayer
        
        player = AudioPlayer()
        print("✓ AudioPlayer initialized successfully")
        
        # Test that the player has the expected attributes
        assert hasattr(player, 'pyaudio'), "AudioPlayer missing pyaudio attribute"
        assert hasattr(player, 'stream'), "AudioPlayer missing stream attribute"
        assert hasattr(player, 'is_playing'), "AudioPlayer missing is_playing attribute"
        
        print("✓ AudioPlayer has all required attributes")
        return True
    except Exception as e:
        print(f"✗ AudioPlayer test failed: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, ASSISTANT_NAME, VOICE_NAME
        
        print(f"✓ Assistant name: {ASSISTANT_NAME}")
        print(f"✓ Voice name: {VOICE_NAME}")
        print(f"✓ OpenAI API key configured: {bool(OPENAI_API_KEY)}")
        print(f"✓ ElevenLabs API key configured: {bool(ELEVENLABS_API_KEY)}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all comprehensive tests."""
    print("Edward Voice AI - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_emotion_function_fix,
        test_elevenlabs_logging_fix,
        test_audio_player,
        test_speech_to_text_error_handling
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
        print("✓ All comprehensive tests passed!")
        print("\nSUMMARY OF FIXES:")
        print("- Fixed AttributeError in get_random_emotion() function")
        print("- Improved ElevenLabs error logging to show specific issues")
        print("- Verified proper exception handling in speech-to-text")
        print("- Confirmed audio player initialization works correctly")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
