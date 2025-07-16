"""
Audio recording module for capturing microphone input.

This module provides the AudioRecorder class which handles microphone
recording with real-time level monitoring and Spotify integration.
"""

import sys
import time
import threading
from typing import Optional

import numpy as np
import sounddevice as sd

from ..integrations.spotify_control import SpotifyController


class AudioRecorder:
    """Handles audio recording from microphone with level monitoring."""
    
    def __init__(self, sample_rate: int = 16000, input_device: Optional[int] = None,
                 no_spotify_control: bool = False):
        """
        Initialize the audio recorder.

        Args:
            sample_rate (int): Audio sample rate in Hz.
            input_device (Optional[int]): Specific audio input device to use.
            no_spotify_control (bool): Whether to disable Spotify integration.
        """
        self.sample_rate = sample_rate
        self.input_device = input_device
        self.spotify_controller = None if no_spotify_control else SpotifyController()
        self.spotify_was_playing = False
        self._stop_signal = threading.Event()
        self._current_level = 0.0
        
        # Show available audio devices if requested
        if input_device == -1:
            self.list_audio_devices()
            sys.exit(0)
    
    def list_audio_devices(self) -> None:
        """List available audio input devices."""
        print("\n🎤 Available Audio Input Devices:")
        print("-" * 50)
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                default = " (DEFAULT)" if i == sd.default.device[0] else ""
                print(f"{i}: {device['name']}{default}")
                print(f"   Channels: {device['max_input_channels']}")
        print("\nUse --device <number> to select a specific device")
    
    def _setup_spotify_pause(self) -> None:
        """Check and pause Spotify if it's playing."""
        if self.spotify_controller:
            self.spotify_was_playing = self.spotify_controller.check_playing()
            if self.spotify_was_playing:
                print("⏸️  Pausing Spotify during recording...")
                self.spotify_controller.pause()
                time.sleep(0.5)  # Brief pause to ensure Spotify has stopped
    
    def _restore_spotify_playback(self) -> None:
        """Resume Spotify playback if it was playing before recording."""
        if self.spotify_controller and self.spotify_was_playing:
            print("\n▶️  Resuming Spotify playback...")
            self.spotify_controller.play()
    
    def stop_recording(self) -> None:
        """Signal the recording to stop gracefully."""
        self._stop_signal.set()
    
    def reset_stop_signal(self) -> None:
        """Reset the stop signal for a new recording."""
        self._stop_signal.clear()
    
    def record_audio(self, duration: int = 5, show_level: bool = True) -> Optional[np.ndarray]:
        """
        Record audio from microphone with graceful stop support.

        Args:
            duration (int): Maximum recording duration in seconds.
            show_level (bool): Whether to show real-time audio level.

        Returns:
            Optional[np.ndarray]: Recorded audio data, or None if recording failed.
        """
        # Reset stop signal for new recording
        self.reset_stop_signal()
        
        # Check and pause Spotify if playing
        self._setup_spotify_pause()
        
        print(f"\n🎤 Recording for up to {duration} seconds...")
        print("   Press Ctrl+C to stop early or call stop_recording() for graceful stop")
        
        audio_data = []
        start_time = time.time()
        recording_stopped = False
        
        def callback(indata, frames, time_info, status):
            """Callback function for audio stream processing."""
            nonlocal recording_stopped
            
            # Check if we should stop recording
            if self._stop_signal.is_set():
                recording_stopped = True
                return
            
            audio_data.append(indata.copy())
            if show_level:
                # Show audio level with increased sensitivity
                level = np.abs(indata).mean()
                self._current_level = level  # Store for TUI access
                bars = int(level * 500)  # Increased from 200 for better sensitivity
                bars = min(bars, 50)  # Cap at 50
                
                # Calculate elapsed time
                elapsed = time.time() - start_time
                elapsed_str = f"{int(elapsed)}s"
                remaining = max(0, duration - elapsed)
                remaining_str = f"{int(remaining)}s"
                
                print(f"\r   📊 Level: {'█' * bars}{' ' * (50-bars)} | ⏱️  {elapsed_str}/{duration}s | ⏳ {remaining_str} left", 
                      end='', flush=True)
        
        try:
            # Adjust input device parameters for better sensitivity
            with sd.InputStream(
                samplerate=self.sample_rate, 
                channels=1,
                callback=callback, 
                dtype='float32',
                device=self.input_device,  # Use specified device if any
                blocksize=1024,  # Smaller blocksize for more responsive level meter
                latency='low'    # Low latency for better responsiveness
            ):
                # Check stop signal every 0.1 seconds instead of sleeping for full duration
                elapsed = 0
                while elapsed < duration and not self._stop_signal.is_set():
                    time.sleep(0.1)
                    elapsed = time.time() - start_time
                
                if self._stop_signal.is_set():
                    elapsed = time.time() - start_time
                    print(f"\n⏹  Recording stopped gracefully at {elapsed:.1f} seconds")
                else:
                    print(f"\n⏰ Recording completed at {duration} seconds")
                    
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            print(f"\n⏹  Recording interrupted at {int(elapsed)} seconds")
        finally:
            # Resume Spotify if it was playing
            self._restore_spotify_playback()
        
        if audio_data:
            total_seconds = len(audio_data) * 1024 / self.sample_rate  # Approximate
            print(f"✅ Processing {len(audio_data)} audio chunks (~{total_seconds:.1f} seconds)")
            return np.concatenate(audio_data, axis=0)
        else:
            print("❌ No audio data recorded")
            return None
    
    def get_current_level(self) -> float:
        """
        Get current audio level for real-time monitoring.
        
        Returns:
            float: Current audio level (0.0 to 1.0).
        """
        if hasattr(self, '_current_level'):
            return self._current_level
        return 0.0