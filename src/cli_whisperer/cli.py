"""
Main CLI application controller that orchestrates all components.

This module provides the CLIApplication class which coordinates the
audio recording, transcription, formatting, and file management
components to provide the complete voice-to-text functionality.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

from .core.audio_recorder import AudioRecorder
from .core.file_manager import TranscriptManager
from .core.formatter import OpenAIFormatter
from .core.transcriber import WhisperTranscriber
from .integrations.clipboard import ClipboardManager
from .ui.ui_manager import UIManager
from .utils.config import DEFAULT_TRANSCRIPT_DIR, MIN_RECORDING_LENGTH, get_transcript_dir
from .utils.history import HistoryManager


class CLIApplication:
    """Main application class that orchestrates all voice-to-text functionality."""
    
    def __init__(self, model_name: str = "base", no_openai: bool = False,
                 openai_model: str = "gpt-4.1-nano", openai_api_key: Optional[str] = None,
                 input_device: Optional[int] = None, no_spotify_control: bool = False,
                 max_recent: int = 5, cleanup_days: int = 7, single_run: bool = False,
                 output_dir: Optional[str] = None):
        """
        Initialize the CLI application with all components.

        Args:
            model_name (str): Whisper model to use for transcription.
            no_openai (bool): Whether to disable OpenAI formatting.
            openai_model (str): OpenAI model to use for formatting.
            openai_api_key (Optional[str]): OpenAI API key.
            input_device (Optional[int]): Audio input device number.
            no_spotify_control (bool): Whether to disable Spotify integration.
            max_recent (int): Maximum number of recent files to keep.
            cleanup_days (int): Number of days after which to cleanup old files.
            single_run (bool): Whether this is a single-run operation.
            output_dir (Optional[str]): Directory to save transcripts.
        """
        # Initialize UI manager
        self.ui = UIManager(single_run=single_run)
        
        # Initialize core components
        # Determine output directory and detect TUI mode
        is_tui_mode = not single_run and self.ui.is_textual_mode()
        
        if output_dir:
            transcript_dir = Path(output_dir)
        else:
            transcript_dir = get_transcript_dir(tui_mode=is_tui_mode)
            
        self.transcript_manager = TranscriptManager(
            base_dir=transcript_dir,
            max_recent=max_recent,
            cleanup_days=cleanup_days
        )
        
        self.transcriber = WhisperTranscriber(model_name=model_name)
        
        self.formatter = OpenAIFormatter(
            model=openai_model,
            api_key=openai_api_key,
            disabled=no_openai
        )
        
        self.audio_recorder = AudioRecorder(
            input_device=input_device,
            no_spotify_control=no_spotify_control
        )
        
        # Initialize utility components
        self.clipboard_manager = ClipboardManager()
        self.history_manager = HistoryManager(
            history_file=self.transcript_manager.base_dir / "history.json"
        )
        
        # Show initialization status through UI
        self.ui.show_initialization(
            model_name=model_name,
            transcript_dir=self.transcript_manager.base_dir,
            openai_enabled=not self.formatter.disabled,
            spotify_enabled=not no_spotify_control
        )
    
    def _save_transcription(self, text: str, formatted_text: Optional[str] = None) -> Tuple[Path, Optional[Path]]:
        """
        Save both raw and formatted transcriptions.

        Args:
            text (str): Raw transcription text.
            formatted_text (Optional[str]): Formatted markdown text.

        Returns:
            Tuple[Path, Optional[Path]]: Paths to saved text and markdown files.
        """
        # Save raw text
        txt_path = self.transcript_manager.save_transcript(text, is_ai=False)
        self.ui.show_file_saved(txt_path, "raw transcription")
        
        md_path = None
        if formatted_text:
            # Save formatted markdown
            md_path = self.transcript_manager.save_transcript(formatted_text, is_ai=True)
            self.ui.show_file_saved(md_path, "formatted markdown")
        
        return txt_path, md_path
    
    def _process_transcription(self, text: str) -> Tuple[Path, Optional[Path]]:
        """
        Process a transcription through formatting, saving, and clipboard operations.

        Args:
            text (str): Raw transcription text.

        Returns:
            Tuple[Path, Optional[Path]]: Paths to saved files.
        """
        # Display raw transcription
        self.ui.show_transcription_result(text)
        
        # Format with OpenAI if enabled
        formatted_text = None
        if not self.formatter.disabled:
            with self.ui.show_openai_formatting_start():
                formatted_text = self.formatter.format_text(
                    text, 
                    cleanup_callback=self.transcript_manager.cleanup_old_files
                )
            
            if formatted_text:
                self.ui.show_openai_formatting_complete()
                self.ui.show_formatted_result(formatted_text)
            else:
                self.ui.show_openai_formatting_failed("No response received")
        
        # Save files
        txt_path, md_path = self._save_transcription(text, formatted_text)
        
        # Copy to clipboard (formatted if available, otherwise raw)
        clipboard_text = formatted_text if formatted_text else text
        success = self.clipboard_manager.copy_to_clipboard(clipboard_text)
        if success:
            self.ui.show_clipboard_success()
        else:
            self.ui.show_clipboard_failed("Unknown error")
        
        # Save to history
        self.history_manager.save_to_history(
            text, txt_path, self.transcriber.model_name, md_path, os.getcwd()
        )
        
        return txt_path, md_path
    
    def record_once(self, duration: int = 5) -> Optional[str]:
        """
        Record once and return transcription.

        Args:
            duration (int): Recording duration in seconds.

        Returns:
            Optional[str]: Transcribed text, or None if recording/transcription failed.
        """
        # Show minimum recording length tip
        print(f"💡 Minimum recording length: {MIN_RECORDING_LENGTH} second(s)")
        
        # Record
        audio_data = self.audio_recorder.record_audio(duration)
        if audio_data is None:
            return None
        
        # Check minimum recording length
        audio_duration = len(audio_data) / self.audio_recorder.sample_rate
        if audio_duration < MIN_RECORDING_LENGTH:
            print(f"❌ Recording too short ({audio_duration:.1f}s) - minimum length is {MIN_RECORDING_LENGTH} second(s)")
            return None
        
        # Transcribe
        estimated_time = self.transcriber._estimate_processing_time(audio_duration)
        
        self.ui.show_transcription_start(int(audio_duration), int(estimated_time))
        
        with self.ui.show_transcription_progress(int(estimated_time)):
            text = self.transcriber.transcribe_audio(audio_data)
        
        if not text:
            self.ui.show_no_speech_detected()
            return None
        
        # Process transcription
        self._process_transcription(text)
        
        return text
    
    def continuous_mode(self, duration: int = 5) -> None:
        """
        Run in continuous mode.

        Args:
            duration (int): Recording duration in seconds for each session.
        """
        # Check if we're using Textual TUI
        if self.ui.is_textual_mode():
            # Set up TUI with components
            self.ui.ui_instance.set_components(
                self.audio_recorder,
                self.transcriber,
                self.formatter,
                self.transcript_manager,
                self.history_manager,
                self.clipboard_manager
            )
            # Set recording duration
            self.ui.ui_instance.set_recording_duration(duration)
            # Run TUI
            self.ui.ui_instance.run()
        else:
            # Use Rich terminal mode
            self.ui.print("\n🔄 [bold blue]Continuous mode[/bold blue] - Press Ctrl+C to exit")
            self.ui.print("   Press Enter to record, or 'q' to quit\n")
            
            while True:
                try:
                    choice = input("Ready to record (Enter/q): ").strip().lower()
                    if choice == 'q':
                        break
                    
                    # Record
                    audio_data = self.audio_recorder.record_audio(duration)
                    if audio_data is None:
                        continue
                    
                    # Transcribe
                    audio_duration = len(audio_data) / self.audio_recorder.sample_rate
                    estimated_time = self.transcriber._estimate_processing_time(audio_duration)
                    
                    self.ui.show_transcription_start(int(audio_duration), int(estimated_time))
                    
                    with self.ui.show_transcription_progress(int(estimated_time)):
                        text = self.transcriber.transcribe_audio(audio_data)
                    
                    if not text:
                        self.ui.show_no_speech_detected()
                        continue
                    
                    # Process transcription
                    self._process_transcription(text)
                    
                except KeyboardInterrupt:
                    self.ui.print("\n\n👋 [yellow]Exiting...[/yellow]")
                    break
    
    def show_history(self, n: int = 10) -> None:
        """
        Show recent transcriptions.

        Args:
            n (int): Number of recent transcriptions to show.
        """
        # Get history data and delegate to UI
        try:
            import json
            if self.history_manager.history_file.exists():
                with open(self.history_manager.history_file, 'r') as f:
                    history = json.load(f)
                self.ui.show_history(history, n)
            else:
                self.ui.show_history([], n)
        except Exception as e:
            self.ui.show_error(f"Failed to read history: {e}")