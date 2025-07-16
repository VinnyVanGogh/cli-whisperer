"""
Rich terminal output formatting for CLI Whisperer single-run mode.

This module provides enhanced terminal output using the Rich library
for single-run operations, offering progress bars, styled text, and
beautiful formatting for better user experience.
"""

import time
from pathlib import Path
from typing import Optional

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.status import Status
from rich.text import Text


class RichOutput:
    """Rich terminal output manager for single-run operations."""
    
    def __init__(self):
        """Initialize the Rich output manager."""
        self.console = Console()
    
    def show_initialization(self, model_name: str, transcript_dir: Path, 
                          openai_enabled: bool, spotify_enabled: bool) -> None:
        """
        Show application initialization status.

        Args:
            model_name (str): Name of the Whisper model being loaded.
            transcript_dir (Path): Directory where transcripts will be saved.
            openai_enabled (bool): Whether OpenAI formatting is enabled.
            spotify_enabled (bool): Whether Spotify control is enabled.
        """
        self.console.print("\n[bold cyan]🎤 CLI Whisperer[/bold cyan] - Voice to Text Tool")
        self.console.print("=" * 50)
        
        # Model loading with status
        with self.console.status(f"[bold blue]Loading Whisper {model_name} model...", spinner="dots"):
            time.sleep(0.5)  # Brief pause to show the spinner
        
        self.console.print(f"✅ [green]Model loaded![/green] Using Whisper {model_name}")
        self.console.print(f"📁 [blue]Transcripts will be saved in:[/blue] {transcript_dir}")
        
        if openai_enabled:
            self.console.print("🤖 [green]OpenAI formatting enabled[/green]")
        
        if spotify_enabled:
            self.console.print("🎵 [green]Spotify auto-pause enabled[/green]")
        
        self.console.print()
    
    def show_audio_devices(self, devices: list) -> None:
        """
        Display available audio input devices.

        Args:
            devices (list): List of audio device information.
        """
        self.console.print("\n🎤 [bold]Available Audio Input Devices:[/bold]")
        self.console.print("─" * 50)
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                default_marker = " [yellow](DEFAULT)[/yellow]" if i == 0 else ""
                self.console.print(f"[cyan]{i}:[/cyan] {device['name']}{default_marker}")
                self.console.print(f"   [dim]Channels: {device['max_input_channels']}[/dim]")
        
        self.console.print("\nUse --device <number> to select a specific device")
    
    def show_recording_start(self, duration: int, spotify_paused: bool = False) -> None:
        """
        Show recording start message.

        Args:
            duration (int): Recording duration in seconds.
            spotify_paused (bool): Whether Spotify was paused.
        """
        if spotify_paused:
            self.console.print("⏸️  [yellow]Pausing Spotify during recording...[/yellow]")
        
        self.console.print(f"\n🎤 [bold green]Recording for {duration} seconds...[/bold green]")
        self.console.print("   [dim]Press Ctrl+C to stop early[/dim]")
    
    def show_audio_level_meter(self, level: float, elapsed: int, duration: int, remaining: int) -> None:
        """
        Display real-time audio level meter.

        Args:
            level (float): Audio level (0.0 to 1.0).
            elapsed (int): Elapsed recording time in seconds.
            duration (int): Total recording duration in seconds.
            remaining (int): Remaining recording time in seconds.
        """
        # Create visual level meter
        bars = int(level * 50)
        meter = "█" * bars + "░" * (50 - bars)
        
        # Color the meter based on level
        if level > 0.7:
            meter_color = "red"
        elif level > 0.3:
            meter_color = "yellow"
        else:
            meter_color = "green"
        
        meter_text = f"[{meter_color}]{meter}[/{meter_color}]"
        
        # Time display
        time_info = f"⏱️  {elapsed}s/{duration}s | ⏳ {remaining}s left"
        
        # Update the line in place
        self.console.print(f"\r   📊 Level: {meter_text} | {time_info}", end="")
    
    def show_recording_complete(self, actual_duration: float) -> None:
        """
        Show recording completion message.

        Args:
            actual_duration (float): Actual recording duration in seconds.
        """
        self.console.print(f"\n✅ [green]Recording complete![/green] (~{int(actual_duration)} seconds of audio)")
        
    def show_recording_stopped_early(self, elapsed: int) -> None:
        """
        Show early recording stop message.

        Args:
            elapsed (int): Elapsed recording time when stopped.
        """
        self.console.print(f"\n⏹  [yellow]Recording stopped early at {elapsed} seconds[/yellow]")
    
    def show_transcription_start(self, audio_duration: int, estimated_time: int) -> None:
        """
        Show transcription start with progress estimation.

        Args:
            audio_duration (int): Duration of audio to transcribe in seconds.
            estimated_time (int): Estimated processing time in seconds.
        """
        self.console.print(f"\n🔄 [blue]Transcribing {audio_duration} seconds of audio...[/blue]")
        self.console.print(f"⏱️  [dim]Estimated processing time: ~{estimated_time} seconds[/dim]")
    
    def show_transcription_progress(self, estimated_time: int) -> Status:
        """
        Show transcription progress with spinner.

        Args:
            estimated_time (int): Estimated processing time.

        Returns:
            Status: Rich status context manager.
        """
        return self.console.status(
            f"[bold blue]Processing with Whisper... (~{estimated_time}s estimated)", 
            spinner="dots"
        )
    
    def show_transcription_complete(self, elapsed_time: float) -> None:
        """
        Show transcription completion message.

        Args:
            elapsed_time (float): Actual transcription time.
        """
        self.console.print(f"✅ [green]Transcription complete in {elapsed_time:.1f} seconds![/green]")
    
    def show_transcription_failed(self, error: str) -> None:
        """
        Show transcription failure message.

        Args:
            error (str): Error message.
        """
        self.console.print(f"❌ [red]Transcription failed:[/red] {error}")
    
    def show_transcription_result(self, text: str) -> None:
        """
        Display the transcription result in a formatted panel.

        Args:
            text (str): Transcribed text.
        """
        self.console.print("\n📝 [bold]Transcription:[/bold]")
        transcription_panel = Panel(
            text,
            title="Raw Transcription",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(transcription_panel)
    
    def show_openai_formatting_start(self) -> Status:
        """
        Show OpenAI formatting start message.

        Returns:
            Status: Rich status context manager.
        """
        return self.console.status("[bold magenta]🤖 Formatting with OpenAI...", spinner="dots")
    
    def show_openai_formatting_complete(self) -> None:
        """Show OpenAI formatting completion message."""
        self.console.print("✅ [green]OpenAI formatting complete![/green]")
    
    def show_openai_formatting_failed(self, error: str) -> None:
        """
        Show OpenAI formatting failure message.

        Args:
            error (str): Error message.
        """
        self.console.print(f"❌ [red]OpenAI formatting failed:[/red] {error}")
    
    def show_formatted_result(self, formatted_text: str) -> None:
        """
        Display the formatted result in a panel.

        Args:
            formatted_text (str): AI-formatted text.
        """
        formatted_panel = Panel(
            formatted_text,
            title="✨ AI-Formatted",
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(formatted_panel)
    
    def show_file_saved(self, file_path: Path, file_type: str) -> None:
        """
        Show file save confirmation.

        Args:
            file_path (Path): Path to saved file.
            file_type (str): Type of file (e.g., "raw transcription", "formatted markdown").
        """
        emoji = "📝" if file_type.startswith("formatted") else "💾"
        self.console.print(f"{emoji} [green]Saved {file_type}:[/green] {file_path}")
    
    def show_clipboard_success(self) -> None:
        """Show clipboard copy success message."""
        self.console.print("📋 [green]Copied to clipboard![/green]")
    
    def show_clipboard_failed(self, error: str) -> None:
        """
        Show clipboard copy failure message.

        Args:
            error (str): Error message.
        """
        self.console.print(f"❌ [red]Failed to copy to clipboard:[/red] {error}")
    
    def show_spotify_resumed(self) -> None:
        """Show Spotify resume message."""
        self.console.print("▶️  [green]Resuming Spotify playback...[/green]")
    
    def show_no_speech_detected(self) -> None:
        """Show no speech detected warning."""
        self.console.print("⚠️  [yellow]No speech detected[/yellow]")
    
    def show_history(self, history_entries: list, count: int) -> None:
        """
        Display transcription history.

        Args:
            history_entries (list): List of history entries.
            count (int): Number of entries to show.
        """
        if not history_entries:
            self.console.print("📜 [yellow]No history found[/yellow]")
            return
        
        self.console.print(f"\n📜 [bold]Recent transcriptions (showing last {count}):[/bold]")
        self.console.print("─" * 80)
        
        for i, entry in enumerate(history_entries[:count]):
            timestamp = entry['timestamp']
            text = entry['text']
            txt_file = Path(entry['txt_file']).name
            md_file = Path(entry['md_file']).name if entry.get('md_file') else "N/A"
            
            self.console.print(f"\n[cyan]{i+1}.[/cyan] [dim][{timestamp}][/dim]")
            self.console.print(f"   [white]Text:[/white] {text}")
            self.console.print(f"   [blue]Files:[/blue] {txt_file} | {md_file}")
    
    def show_error(self, message: str) -> None:
        """
        Show error message.

        Args:
            message (str): Error message.
        """
        self.console.print(f"❌ [red]Error:[/red] {message}")
    
    def show_warning(self, message: str) -> None:
        """
        Show warning message.

        Args:
            message (str): Warning message.
        """
        self.console.print(f"⚠️  [yellow]Warning:[/yellow] {message}")
    
    def show_info(self, message: str) -> None:
        """
        Show info message.

        Args:
            message (str): Info message.
        """
        self.console.print(f"ℹ️  [blue]Info:[/blue] {message}")
    
    def print(self, *args, **kwargs) -> None:
        """
        Print using Rich console.

        Args:
            *args: Arguments to pass to console.print.
            **kwargs: Keyword arguments to pass to console.print.
        """
        self.console.print(*args, **kwargs)
    
    def print_panel(self, content: str, title: str = "", style: str = "blue") -> None:
        """
        Print content in a panel.

        Args:
            content (str): Content to display.
            title (str): Panel title.
            style (str): Panel border style.
        """
        panel = Panel(content, title=title, border_style=style)
        self.console.print(panel)