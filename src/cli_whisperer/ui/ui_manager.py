"""
UI Manager for CLI Whisperer.

This module determines which UI mode to use based on the operation type
and provides a unified interface for UI operations.
"""

from typing import Optional, Dict, Any

from .rich_output import RichOutput


class UIManager:
    """
    Manages UI mode selection and provides unified interface.
    
    Decides between Rich terminal output for single runs and
    Textual TUI for continuous interactive sessions.
    """
    
    def __init__(self, single_run: bool = False):
        """
        Initialize the UI manager.

        Args:
            single_run (bool): Whether this is a single-run operation.
        """
        self.single_run = single_run
        self.ui_mode = self._determine_ui_mode(single_run)
        self.ui_instance = self._create_ui_instance()
    
    def _determine_ui_mode(self, single_run: bool) -> str:
        """
        Determine which UI mode to use.

        Args:
            single_run (bool): Whether this is a single-run operation.

        Returns:
            str: UI mode ("rich" or "textual").
        """
        if single_run:
            return "rich"
        else:
            return "textual"
    
    def _create_ui_instance(self):
        """
        Create the appropriate UI instance.

        Returns:
            UI instance based on the determined mode.
        """
        if self.ui_mode == "rich":
            return RichOutput()
        elif self.ui_mode == "textual":
            from .textual_app import TextualTUI
            return TextualTUI()
        else:
            raise ValueError(f"Unknown UI mode: {self.ui_mode}")
    
    def is_rich_mode(self) -> bool:
        """
        Check if currently using Rich output mode.

        Returns:
            bool: True if using Rich mode.
        """
        return self.ui_mode == "rich"
    
    def is_textual_mode(self) -> bool:
        """
        Check if currently using Textual TUI mode.

        Returns:
            bool: True if using Textual mode.
        """
        return self.ui_mode == "textual"
    
    def get_ui(self):
        """
        Get the UI instance.

        Returns:
            UI instance for the current mode.
        """
        return self.ui_instance
    
    # Delegate common UI methods to the underlying UI instance
    def show_initialization(self, *args, **kwargs):
        """Show application initialization status."""
        return self.ui_instance.show_initialization(*args, **kwargs)
    
    def show_audio_devices(self, *args, **kwargs):
        """Display available audio input devices."""
        return self.ui_instance.show_audio_devices(*args, **kwargs)
    
    def show_recording_start(self, *args, **kwargs):
        """Show recording start message."""
        return self.ui_instance.show_recording_start(*args, **kwargs)
    
    def show_audio_level_meter(self, *args, **kwargs):
        """Display real-time audio level meter."""
        return self.ui_instance.show_audio_level_meter(*args, **kwargs)
    
    def show_recording_complete(self, *args, **kwargs):
        """Show recording completion message."""
        return self.ui_instance.show_recording_complete(*args, **kwargs)
    
    def show_recording_stopped_early(self, *args, **kwargs):
        """Show early recording stop message."""
        return self.ui_instance.show_recording_stopped_early(*args, **kwargs)
    
    def show_transcription_start(self, *args, **kwargs):
        """Show transcription start with progress estimation."""
        return self.ui_instance.show_transcription_start(*args, **kwargs)
    
    def show_transcription_progress(self, *args, **kwargs):
        """Show transcription progress with spinner."""
        return self.ui_instance.show_transcription_progress(*args, **kwargs)
    
    def show_transcription_complete(self, *args, **kwargs):
        """Show transcription completion message."""
        return self.ui_instance.show_transcription_complete(*args, **kwargs)
    
    def show_transcription_failed(self, *args, **kwargs):
        """Show transcription failure message."""
        return self.ui_instance.show_transcription_failed(*args, **kwargs)
    
    def show_transcription_result(self, *args, **kwargs):
        """Display the transcription result."""
        return self.ui_instance.show_transcription_result(*args, **kwargs)
    
    def show_openai_formatting_start(self, *args, **kwargs):
        """Show OpenAI formatting start message."""
        return self.ui_instance.show_openai_formatting_start(*args, **kwargs)
    
    def show_openai_formatting_complete(self, *args, **kwargs):
        """Show OpenAI formatting completion message."""
        return self.ui_instance.show_openai_formatting_complete(*args, **kwargs)
    
    def show_openai_formatting_failed(self, *args, **kwargs):
        """Show OpenAI formatting failure message."""
        return self.ui_instance.show_openai_formatting_failed(*args, **kwargs)
    
    def show_formatted_result(self, *args, **kwargs):
        """Display the formatted result."""
        return self.ui_instance.show_formatted_result(*args, **kwargs)
    
    def show_file_saved(self, *args, **kwargs):
        """Show file save confirmation."""
        return self.ui_instance.show_file_saved(*args, **kwargs)
    
    def show_clipboard_success(self, *args, **kwargs):
        """Show clipboard copy success message."""
        return self.ui_instance.show_clipboard_success(*args, **kwargs)
    
    def show_clipboard_failed(self, *args, **kwargs):
        """Show clipboard copy failure message."""
        return self.ui_instance.show_clipboard_failed(*args, **kwargs)
    
    def show_spotify_resumed(self, *args, **kwargs):
        """Show Spotify resume message."""
        return self.ui_instance.show_spotify_resumed(*args, **kwargs)
    
    def show_no_speech_detected(self, *args, **kwargs):
        """Show no speech detected warning."""
        return self.ui_instance.show_no_speech_detected(*args, **kwargs)
    
    def show_history(self, *args, **kwargs):
        """Display transcription history."""
        return self.ui_instance.show_history(*args, **kwargs)
    
    def show_error(self, *args, **kwargs):
        """Show error message."""
        return self.ui_instance.show_error(*args, **kwargs)
    
    def show_warning(self, *args, **kwargs):
        """Show warning message."""
        return self.ui_instance.show_warning(*args, **kwargs)
    
    def show_info(self, *args, **kwargs):
        """Show info message."""
        return self.ui_instance.show_info(*args, **kwargs)
    
    def print(self, *args, **kwargs):
        """Print using the current UI."""
        return self.ui_instance.print(*args, **kwargs)