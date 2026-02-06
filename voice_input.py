import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from vad import record_until_silence

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def record_voice(filename="audio/voice.wav", duration=5, use_vad=True, stop_event=None):
    """
    Record voice with optional Voice Activity Detection (VAD).
    
    Args:
        filename: Output filename for the recording
        duration: Maximum recording duration in seconds (used if VAD is disabled)
        use_vad: Whether to use Voice Activity Detection
        stop_event: Optional threading.Event to stop recording early
        
    Returns:
        str: Path to the recorded audio file
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(filename)
    if output_dir:
        ensure_dir(output_dir)
    
    sample_rate = 16000  # Standard sample rate for speech recognition
    
    if use_vad:
        print("Listening... (speak now, I'll detect when you're done)")
        audio = record_until_silence(
            sample_rate=sample_rate,
            silence_duration=1.0,  # Stop after 1 second of silence
            max_duration=duration  # Maximum recording duration
        )
        
        if len(audio) > 0:
            # Convert to 16-bit PCM for better compatibility
            audio_int16 = (audio * 32767).astype(np.int16)
            write(filename, sample_rate, audio_int16)
            print(f"Recording complete. Saved to {filename}")
            return filename
        else:
            print("No speech detected.")
            return None
    else:
        # Fallback to fixed-duration recording if VAD is disabled
        print(f"Speak now (recording for {duration} seconds)...")
        audio = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1,
                      dtype='float32')
        sd.wait()
        
        # Convert to 16-bit PCM for better compatibility
        audio_int16 = (audio * 32767).astype(np.int16)
        write(filename, sample_rate, audio_int16)
        print(f"Recording complete. Saved to {filename}")
        return filename

if __name__ == "__main__":
    # Test the recording
    print("Testing voice recording with VAD...")
    record_voice("test_recording.wav")
