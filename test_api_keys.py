from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, ASSISTANT_NAME, VOICE_NAME

def test_api_keys():
    print("Testing API Key Configuration...")
    print("-" * 30)
    print(f"Assistant Name: {ASSISTANT_NAME}")
    print(f"Voice Name: {VOICE_NAME}")
    print(f"OpenAI API Key: {'Set' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here' else 'Not Set'}")
    print(f"ElevenLabs API Key: {'Set' if ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != 'your_elevenlabs_api_key_here' else 'Not Set'}")

if __name__ == "__main__":
    test_api_keys()
