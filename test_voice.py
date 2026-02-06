from voice_manager import voice_manager

def test_voice():
    print("Testing voice synthesis...")
    
    # List available voices
    print("\nAvailable voices:")
    voices = voice_manager.list_available_voices()
    for i, voice in enumerate(voices, 1):
        print(f"{i}. {voice}")
    
    # Test text to speech
    test_text = "Hello! This is a test of the voice synthesis system. How does it sound?"
    print(f"\nSaying: {test_text}")
    
    # Generate and play the speech
    audio = voice_manager.text_to_speech(test_text)
    if audio:
        print("Playing audio...")
        voice_manager.play_audio(audio)
        print("Test completed successfully!")
    else:
        print("Failed to generate speech.")

if __name__ == "__main__":
    test_voice()
