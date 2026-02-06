#!/usr/bin/env python3
"""
Test to verify the voice synthesis fixes are working.
"""
import sys
import traceback

def test_voice_manager_fixes():
    """Test that voice manager handles all scenarios correctly."""
    print("Testing voice manager fixes...")
    
    try:
        from voice_manager import voice_manager
        
        # Test 1: Check that voices are loaded (fallback or real)
        voices = voice_manager.list_available_voices()
        print(f"✓ Available voices: {len(voices)} voices found")
        for voice in voices[:3]:  # Show first 3
            print(f"  - {voice}")
        
        # Test 2: Test text-to-speech with fallback
        test_text = "This is a test of the voice synthesis system."
        print(f"\n✓ Testing TTS with: '{test_text}'")
        
        audio = voice_manager.text_to_speech(test_text)
        if audio:
            print(f"✓ TTS successful, generated {len(audio)} bytes of audio")
            
            # Test 3: Test audio playback
            print("✓ Testing audio playback...")
            voice_manager.play_audio(audio)
            print("✓ Audio playback completed")
        else:
            print("✗ TTS failed")
            return False
        
        # Test 4: Test with different voice names
        for voice_name in voices[:2]:  # Test first 2 voices
            print(f"\n✓ Testing with voice: {voice_name}")
            audio = voice_manager.text_to_speech("Voice test", voice_name)
            if audio:
                print(f"✓ Voice '{voice_name}' works correctly")
            else:
                print(f"✗ Voice '{voice_name}' failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Voice manager test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting error handling...")
    
    try:
        from voice_manager import voice_manager
        
        # Test with empty text
        result = voice_manager.text_to_speech("")
        if result is None:
            print("✓ Empty text handled correctly")
        else:
            print("✗ Empty text should return None")
            return False
        
        # Test with whitespace text
        result = voice_manager.text_to_speech("   ")
        if result is None:
            print("✓ Whitespace text handled correctly")
        else:
            print("✗ Whitespace text should return None")
            return False
        
        # Test with non-existent voice (should fallback to default)
        audio = voice_manager.text_to_speech("Test", "NonExistentVoice")
        if audio:
            print("✓ Non-existent voice falls back correctly")
        else:
            print("✗ Non-existent voice fallback failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def test_fallback_functionality():
    """Test that fallback functionality works when ElevenLabs is unavailable."""
    print("\nTesting fallback functionality...")
    
    try:
        from voice_manager import voice_manager
        
        # Check if we're using fallback voices
        voices = voice_manager.list_available_voices()
        if voices:
            first_voice = voice_manager.voices.get(voices[0])
            
            if hasattr(first_voice, 'voice_id') and first_voice.voice_id.startswith('fallback-'):
                print("✓ Using fallback voices (ElevenLabs unavailable)")
                
                # Test that fallback TTS works
                audio = voice_manager.text_to_speech("Fallback test")
                if audio:
                    print("✓ Fallback TTS generates audio")
                    return True
                else:
                    print("✗ Fallback TTS failed")
                    return False
            else:
                print("✓ Using real ElevenLabs voices")
                return True
        else:
            print("✗ No voices available")
            return False
            
    except Exception as e:
        print(f"✗ Fallback test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all voice tests."""
    print("Edward Voice AI - Voice Synthesis Fix Test")
    print("=" * 50)
    
    tests = [
        test_voice_manager_fixes,
        test_error_handling,
        test_fallback_functionality
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
        print("✓ All voice synthesis tests passed!")
        print("\nSUMMARY OF FIXES:")
        print("- Added fallback voices when ElevenLabs API is unavailable")
        print("- Implemented system TTS fallback using pyttsx3")
        print("- Improved error handling for missing voices")
        print("- Added robust audio playback with multiple fallbacks")
        print("- Graceful degradation when API keys are invalid")
        return 0
    else:
        print("✗ Some voice tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
