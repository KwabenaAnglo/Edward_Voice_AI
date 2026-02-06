# Edward Voice AI

A voice-enabled AI assistant that uses OpenAI for natural language processing and ElevenLabs for text-to-speech capabilities.

## Features
- Voice input and output
- Speech-to-text conversion
- AI-powered responses using OpenAI
- Natural-sounding voice synthesis
- Voice activity detection

## Prerequisites
- Python 3.8+
- PortAudio (for PyAudio)
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Edward_Voice_AI
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API keys to `.env`

## Usage

Run the application:
```bash
python main.py
```

## Configuration

Edit the `.env` file to configure:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `ASSISTANT_NAME`: Name of your AI assistant
- `VOICE_NAME`: Voice to use for text-to-speech
- `DEFAULT_LANGUAGE`: Default language for speech recognition

## Project Structure

- `main.py`: Entry point of the application
- `gui.py`: Graphical user interface
- `ai_brain.py`: AI response generation
- `speech_to_text.py`: Speech recognition
- `text_to_speech.py`: Text-to-speech conversion
- `voice_input.py`: Voice activity detection
- `config.py`: Configuration management
- `utils/`: Utility functions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT
