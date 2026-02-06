# Global variable to track VAD availability
global VAD_AVAILABLE

# Try to import webrtcvad
try:
    import webrtcvad
    from webrtcvad import Vad
    VAD_AVAILABLE = True
except ImportError:
    print("Warning: webrtcvad not available. Voice activity detection will be disabled.")
    VAD_AVAILABLE = False
import numpy as np
import sounddevice as sd
from typing import Optional, Callable

class VoiceActivityDetector:
    """
    A Voice Activity Detection (VAD) class using WebRTC VAD.
    Detects when someone is speaking based on audio input.
    """
    
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 3):
        """
        Initialize the VAD.
        
        Args:
            sample_rate: Audio sample rate in Hz (must be 8000, 16000, 32000, or 48000)
            aggressiveness: Aggressiveness mode (0-3, where 3 is the most aggressive)
        """
        self.sample_rate = sample_rate
        self.is_speaking = False
        self.speech_buffer = []
        
        # WebRTC VAD requires specific frame sizes (10, 20, or 30 ms)
        self.frame_duration = 30  # ms
        self.samples_per_frame = (sample_rate * self.frame_duration) // 1000
        
        # Initialize VAD if available
        self.vad = None
        global VAD_AVAILABLE  # Use the global variable
        if VAD_AVAILABLE:
            try:
                self.vad = Vad(aggressiveness)
            except Exception as e:
                print(f"Warning: Failed to initialize VAD: {e}")
                VAD_AVAILABLE = False
    
    def process_audio(self, audio_data: np.ndarray) -> bool:
        """
        Process an audio frame and update voice activity status.
        
        Args:
            audio_data: Mono audio data as a numpy array (16-bit PCM)
            
        Returns:
            bool: True if voice activity is detected, False otherwise
        """
        # Convert to 16-bit PCM if needed
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # Process in chunks that WebRTC VAD can handle
        is_speech_detected = False
        
        if self.vad is not None:
            for i in range(0, len(audio_data), self.samples_per_frame):
                frame = audio_data[i:i + self.samples_per_frame]
                if len(frame) < self.samples_per_frame:
                    continue
                    
                # VAD requires 16-bit PCM data
                frame_bytes = frame.tobytes()
                try:
                    if self.vad.is_speech(frame_bytes, self.sample_rate):
                        is_speech_detected = True
                        break  # Early exit if speech is detected
                except Exception as e:
                    # Handle cases where VAD processing fails
                    print(f"VAD processing error: {e}")
                    global VAD_AVAILABLE
                    VAD_AVAILABLE = False
                    self.vad = None
                    break
        else:
            # Fallback: Use simple energy-based VAD if WebRTC VAD is not available
            energy = np.mean(np.abs(audio_data))
            is_speech_detected = energy > 0.01  # Simple energy threshold
        
        # Update speech state with some hysteresis
        if is_speech_detected:
            self.speech_buffer.append(True)
            if len(self.speech_buffer) > 3:  # Require multiple detections
                self.is_speaking = True
                self.speech_buffer = self.speech_buffer[-3:]  # Keep buffer size fixed
        else:
            self.speech_buffer.append(False)
            if len(self.speech_buffer) > 5:  # Require more silence to stop
                if not any(self.speech_buffer[-3:]):  # If last 3 frames are silent
                    self.is_speaking = False
                    self.speech_buffer = []
        
        return self.is_speaking

def record_until_silence(
    sample_rate: int = 16000, 
    silence_duration: float = 1.0,
    vad_aggressiveness: int = 3,
    max_duration: float = 30.0,
    callback: Optional[Callable] = None
) -> np.ndarray:
    """
    Record audio until silence is detected.
    
    Args:
        sample_rate: Audio sample rate in Hz
        silence_duration: Seconds of silence to stop recording
        vad_aggressiveness: VAD aggressiveness (0-3)
        max_duration: Maximum recording duration in seconds
        callback: Optional callback function that receives the current audio buffer
        
    Returns:
        np.ndarray: Recorded audio data
    """
    vad = VoiceActivityDetector(sample_rate, vad_aggressiveness)
    audio_buffer = []
    silent_frames = 0
    frames_before_silence = int(silence_duration * sample_rate / 1024)
    max_frames = int(max_duration * sample_rate / 1024)
    
    def audio_callback(indata, frames, time, status):
        nonlocal silent_frames, audio_buffer
        
        # Check for voice activity
        is_speech = vad.process_audio(indata[:, 0]) if indata.size > 0 else False
        
        if is_speech:
            silent_frames = 0
            audio_buffer.append(indata.copy())
        elif len(audio_buffer) > 0:  # Only count silence after speech has started
            silent_frames += 1
            audio_buffer.append(indata.copy())
        
        # Call the user-provided callback if any
        if callback:
            callback(indata, is_speech, silent_frames)
    
    # Start recording
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype='float32',
        blocksize=1024,
        callback=audio_callback
    ) as stream:
        print("Listening... (speak now)")
        while stream.active:
            if (silent_frames >= frames_before_silence and len(audio_buffer) > 0) or \
               (max_frames > 0 and len(audio_buffer) >= max_frames):
                break
            sd.sleep(100)
    
    # Concatenate all audio chunks
    if len(audio_buffer) > 0:
        return np.concatenate(audio_buffer, axis=0)
    return np.array([], dtype=np.float32)

if __name__ == "__main__":
    # Example usage
    print("Testing Voice Activity Detection...")
    print("Speak into your microphone. Recording will stop after 1 second of silence.")
    
    def status_callback(indata, is_speech, silent_frames):
        print(f"\rSpeech: {'YES' if is_speech else 'NO '} | "
              f"Silent frames: {silent_frames:3d}", end="")
    
    audio = record_until_silence(callback=status_callback)
    print("\nRecording complete!")
    
    if len(audio) > 0:
        print(f"Recorded {len(audio)/16000:.2f} seconds of audio")
        # You can save or process the recorded audio here
    else:
        print("No audio recorded")
