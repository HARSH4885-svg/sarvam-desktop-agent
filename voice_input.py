import time
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

class VoiceRecorder:
    """Handles microphone recording for push-to-wake activation."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._stop_event = threading.Event()
        self._recorded_frames = []

    def record_to_file(self, output_path: str = "temp_audio.wav", max_duration: float = 12.0, silence_timeout: float = 1.8) -> bool:
        """
        Record audio from the default microphone until silence is detected or max_duration is reached.
        Returns True if speech was recorded, False if cancelled or empty.
        """
        self.is_recording = True
        self._stop_event.clear()
        self._recorded_frames = []

        chunk_duration = 0.1  # 100ms per block
        chunk_size = int(self.sample_rate * chunk_duration)
        silence_threshold = 0.015  # RMS energy threshold
        
        silence_chunks_needed = int(silence_timeout / chunk_duration)
        consecutive_silence = 0
        has_spoken = False
        start_time = time.time()

        def audio_callback(indata, frames, time_info, status):
            if self.is_recording:
                self._recorded_frames.append(indata.copy())

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=audio_callback):
                while self.is_recording and not self._stop_event.is_set():
                    elapsed = time.time() - start_time
                    if elapsed >= max_duration:
                        break

                    time.sleep(chunk_duration)
                    
                    if len(self._recorded_frames) > 0:
                        recent_chunk = self._recorded_frames[-1]
                        rms = np.sqrt(np.mean(recent_chunk**2))
                        
                        if rms > silence_threshold:
                            has_spoken = True
                            consecutive_silence = 0
                        else:
                            if has_spoken:
                                consecutive_silence += 1
                                if consecutive_silence >= silence_chunks_needed:
                                    # User finished speaking
                                    break
        except Exception as e:
            print(f"[Audio Record Error]: {e}")
            self.is_recording = False
            return False

        self.is_recording = False

        if not self._recorded_frames:
            return False

        # Concatenate audio frames and convert to 16-bit PCM
        audio_data = np.concatenate(self._recorded_frames, axis=0)
        # Normalize and convert to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        write(output_path, self.sample_rate, audio_int16)
        return True

    def stop(self):
        """Signal recording to stop immediately."""
        self.is_recording = False
        self._stop_event.set()
