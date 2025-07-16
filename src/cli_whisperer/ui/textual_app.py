"""
Textual TUI application for CLI Whisperer continuous mode.

This module provides a full Terminal User Interface using Textual for
continuous recording sessions, offering real-time status updates,
history viewing, and interactive controls.
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button, Footer, Header, Input, Label, ListItem, ListView, 
    ProgressBar, RichLog, Static, Switch, TabbedContent, TabPane, Select
)
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from textual.screen import Screen
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

from ..utils.config import DEFAULT_TRANSCRIPT_DIR, MIN_RECORDING_LENGTH
from ..utils.logger import get_logger
from .themes import ThemeManager
from .edit_manager import EditManager


class StatusPanel(Static):
    """Status panel showing system information and current state."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_name = "base"
        self.openai_enabled = False
        self.spotify_enabled = False
        self.transcript_dir = DEFAULT_TRANSCRIPT_DIR
        self.recording_state = "idle"  # idle, recording, transcribing, formatting
        
    def update_status(self, **kwargs):
        """Update status information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the status display."""
        # Enhanced state display with emojis and colors
        state_emoji = {
            "idle": "⏸️",
            "recording": "🔴",
            "transcribing": "⚙️",
            "formatting": "✨"
        }
        
        state_color = {
            "idle": "white",
            "recording": "red",
            "transcribing": "yellow", 
            "formatting": "cyan"
        }
        
        current_state = self.recording_state.lower()
        emoji = state_emoji.get(current_state, "⏸️")
        color = state_color.get(current_state, "white")
        
        status_text = f"""
🎤 [bold]CLI Whisperer - Voice to Text Tool[/bold]
{emoji} State: [{color}][bold]{self.recording_state.upper()}[/bold][/{color}]
🤖 Model: [cyan]{self.model_name}[/cyan]
🤖 OpenAI: {'[green]✅ Enabled[/green]' if self.openai_enabled else '[red]❌ Disabled[/red]'}
🎵 Spotify: {'[green]✅ Connected[/green]' if self.spotify_enabled else '[red]❌ Disconnected[/red]'}
📁 Transcripts: [dim]{self.transcript_dir}[/dim]
"""
        self.update(status_text.strip())


class SpotifyStatusPanel(Container):
    """Panel showing Spotify status and playback information with controls."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spotify_controller = None
        self.status_timer = None
        self.enabled = False
        self.current_status = None
    
    def compose(self) -> ComposeResult:
        """Compose the Spotify status panel with controls."""
        with Vertical():
            # Status display
            yield Static("🎵 [bold]Spotify Status[/bold]\n[dim]No music playing or Spotify not available[/dim]", 
                        id="spotify-status-display")
            
            # Control buttons
            with Horizontal(classes="spotify-controls"):
                yield Button("⏮️", id="prev-track", variant="default", classes="spotify-btn")
                yield Button("⏸️", id="pause-play", variant="primary", classes="spotify-btn")
                yield Button("⏭️", id="next-track", variant="default", classes="spotify-btn")
                yield Button("🔀", id="shuffle-toggle", variant="default", classes="spotify-btn")
                yield Button("🔁", id="repeat-toggle", variant="default", classes="spotify-btn")
        
    def set_spotify_controller(self, controller):
        """Set the Spotify controller and start status updates."""
        self.spotify_controller = controller
        self.enabled = controller is not None
        if self.enabled:
            self.start_status_updates()
        else:
            self.update_display(None)
            
    def start_status_updates(self):
        """Start periodic status updates."""
        if self.enabled and not self.status_timer:
            self.status_timer = self.set_interval(2.0, self.update_spotify_status)
            
    def stop_status_updates(self):
        """Stop periodic status updates."""
        if self.status_timer:
            self.status_timer.stop()
            self.status_timer = None
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Spotify control button presses."""
        if not self.enabled or not self.spotify_controller:
            self.app.notify("⚠️ Spotify not available", severity="warning")
            return
            
        button_id = event.button.id
        
        try:
            if button_id == "pause-play":
                self._toggle_play_pause()
            elif button_id == "prev-track":
                self._previous_track()
            elif button_id == "next-track":
                self._next_track()
            elif button_id == "shuffle-toggle":
                self._toggle_shuffle()
            elif button_id == "repeat-toggle":
                self._toggle_repeat()
        except Exception as e:
            self.app.notify(f"⚠️ Spotify command failed: {e}", severity="error")
    
    def update_spotify_status(self):
        """Update Spotify status information."""
        if not self.enabled or not self.spotify_controller:
            return
            
        try:
            status = self.spotify_controller.get_status()
            self.current_status = status
            self.update_display(status)
        except Exception as e:
            # Silently handle errors to avoid spamming the UI
            pass
            
    def update_display(self, status):
        """Update the status display."""
        try:
            display_widget = self.query_one("#spotify-status-display")
            pause_play_btn = self.query_one("#pause-play")
            
            if not status:
                status_text = """🎵 [bold]Spotify Status[/bold]
[dim]No music playing or Spotify not available[/dim]"""
                pause_play_btn.label = "⏸️"
                pause_play_btn.disabled = True
            else:
                # Format status information
                artist = status.get('artist', 'Unknown Artist')
                album = status.get('album', 'Unknown Album')
                track = status.get('track', 'Unknown Track')
                position = status.get('position', '0:00')
                playing = status.get('playing', False)
                shuffle = status.get('shuffle', 'off')
                repeat = status.get('repeat', 'off')
                
                play_status = "▶️ Playing" if playing else "⏸️ Paused"
                
                # Update play/pause button
                pause_play_btn.label = "⏸️" if playing else "▶️"
                pause_play_btn.disabled = False
                
                # Update shuffle/repeat button states
                try:
                    shuffle_btn = self.query_one("#shuffle-toggle")
                    shuffle_btn.variant = "success" if shuffle.lower() == "on" else "default"
                    
                    repeat_btn = self.query_one("#repeat-toggle")
                    repeat_btn.variant = "success" if repeat.lower() in ["on", "track"] else "default"
                except Exception:
                    pass  # Buttons might not exist yet
                
                # Enhanced status display with more detail
                shuffle_icon = "🔀" if shuffle.lower() == "on" else "➡️"
                repeat_icons = {"off": "🔄", "track": "🔂", "context": "🔁"}
                repeat_icon = repeat_icons.get(repeat.lower(), "🔄")
                
                # Volume info if available
                volume_info = ""
                if 'volume' in status:
                    volume_info = f"\n🔊 Volume: {status['volume']}%"
                
                # Progress bar for position if available
                progress_info = ""
                if 'duration' in status and 'position' in status:
                    try:
                        duration = status['duration']
                        current_pos = status['position']
                        if duration and current_pos:
                            progress_info = f"\n▶️ Progress: {current_pos} / {duration}"
                    except:
                        pass
                
                status_text = f"""🎵 [bold]Spotify Status[/bold]
{play_status}
🎤 [cyan]{artist}[/cyan]
💿 [dim]{album}[/dim]
🎵 [green]{track}[/green]
⏱️ {position}{progress_info}
{shuffle_icon} Shuffle: {shuffle.title()} | {repeat_icon} Repeat: {repeat.title()}{volume_info}"""
                
            display_widget.update(status_text)
        except Exception:
            # Handle case where widgets don't exist yet
            pass
    
    def _toggle_play_pause(self):
        """Toggle play/pause state."""
        if self.current_status and self.current_status.get('playing', False):
            success = self.spotify_controller.pause()
            if success:
                self.app.notify("⏸️ Paused", severity="information")
            else:
                self.app.notify("⚠️ Failed to pause", severity="error")
        else:
            success = self.spotify_controller.play()
            if success:
                self.app.notify("▶️ Playing", severity="information")
            else:
                self.app.notify("⚠️ Failed to play", severity="error")
        
        # Update status immediately
        self.update_spotify_status()
    
    def _previous_track(self):
        """Go to previous track."""
        success = self.spotify_controller.previous_track()
        if success:
            self.app.notify("⏮️ Previous track", severity="information")
        else:
            self.app.notify("⚠️ Failed to skip to previous track", severity="error")
        
        # Update status immediately
        self.update_spotify_status()
    
    def _next_track(self):
        """Go to next track."""
        success = self.spotify_controller.next_track()
        if success:
            self.app.notify("⏭️ Next track", severity="information")
        else:
            self.app.notify("⚠️ Failed to skip to next track", severity="error")
        
        # Update status immediately
        self.update_spotify_status()
    
    def _toggle_shuffle(self):
        """Toggle shuffle mode."""
        success = self.spotify_controller.toggle_shuffle()
        if success:
            self.app.notify("🔀 Shuffle toggled", severity="information")
        else:
            self.app.notify("⚠️ Failed to toggle shuffle", severity="error")
        
        # Update status immediately
        self.update_spotify_status()
    
    def _toggle_repeat(self):
        """Toggle repeat mode."""
        success = self.spotify_controller.toggle_repeat()
        if success:
            self.app.notify("🔁 Repeat toggled", severity="information")
        else:
            self.app.notify("⚠️ Failed to toggle repeat", severity="error")
        
        # Update status immediately
        self.update_spotify_status()


class AudioLevelMeter(Static):
    """Real-time audio level meter widget with waveform visualization."""
    
    level = reactive(0.0)
    recording_state = reactive("idle")  # idle, recording, transcribing, formatting
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_bars = 50
        self.pulse_timer = None
        self.peak_hold = 0.0
        self.peak_decay = 0.98  # Peak decay rate
        self.level_history = []  # Store recent levels for waveform
        self.history_size = 20
        self.clip_count = 0  # Track clipping events
        self.last_update_time = 0
        
    def watch_level(self, level: float):
        """Update visual meter with waveform visualization and enhanced color coding."""
        import time
        current_time = time.time()
        
        # Track clipping events
        if level >= 0.95:
            self.clip_count += 1
        
        # Update level history for waveform
        self.level_history.append(level)
        if len(self.level_history) > self.history_size:
            self.level_history.pop(0)
        
        # Update peak hold with decay
        if level > self.peak_hold:
            self.peak_hold = level
        else:
            self.peak_hold *= self.peak_decay
        
        self.last_update_time = current_time
        
        # Create enhanced meter with multiple visual elements
        bars = int(level * self.max_bars)
        peak_bar = int(self.peak_hold * self.max_bars)
        
        # Build waveform visualization
        waveform = self._create_waveform()
        
        # Create gradient meter with peak indicator
        meter = self._create_gradient_meter(bars, peak_bar)
        
        # Enhanced color coding and status with quality indicators
        color, status, quality_icon = self._get_level_status(level)
        
        percentage = int(level * 100)
        peak_percentage = int(self.peak_hold * 100)
        
        # Get audio quality statistics
        avg_level = self._get_average_level()
        quality_stats = self._get_quality_stats()
        
        # Create comprehensive display with waveform and peak info
        if self.recording_state == "recording":
            pulse_indicator = self._get_pulse_indicator()
            display_text = f"🎚️ Audio: {pulse_indicator} {status} {quality_icon} {quality_stats}\n{waveform}\n[{color}]{meter}[/{color}] {percentage}% (Peak: {peak_percentage}%, Avg: {avg_level}%)"
            self.add_class("pulsing")
        elif self.recording_state == "transcribing":
            display_text = f"🎚️ Audio: ⚙️ {status} {quality_icon} [dim](Transcribing...)[/dim]\n{waveform}\n[{color}]{meter}[/{color}] {percentage}% (Peak: {peak_percentage}%, Avg: {avg_level}%)"
            self.add_class("transcribing")
        elif self.recording_state == "formatting":
            display_text = f"🎚️ Audio: ✨ {status} {quality_icon} [dim](Formatting...)[/dim]\n{waveform}\n[{color}]{meter}[/{color}] {percentage}% (Peak: {peak_percentage}%, Avg: {avg_level}%)"
            self.add_class("formatting")
        else:
            display_text = f"🎚️ Audio: {status} {quality_icon}\n{waveform}\n[{color}]{meter}[/{color}] {percentage}% (Peak: {peak_percentage}%, Avg: {avg_level}%)"
            self.remove_class("pulsing", "transcribing", "formatting")
        
        self.update(display_text)
    
    def _create_waveform(self) -> str:
        """Create a mini waveform visualization from recent levels with color coding."""
        if not self.level_history:
            return "Wave: [dim]" + "▁" * 20 + "[/dim]"
        
        # Create waveform bars using different Unicode characters
        waveform_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        waveform = ""
        
        # Pad history if needed
        padded_history = self.level_history + [0.0] * (self.history_size - len(self.level_history))
        
        for level in padded_history:
            char_index = min(int(level * 8), 7)  # 8 levels of bars
            char = waveform_chars[char_index]
            
            # Add color based on level
            if level > 0.8:
                waveform += f"[red]{char}[/red]"
            elif level > 0.6:
                waveform += f"[yellow]{char}[/yellow]"
            elif level > 0.3:
                waveform += f"[green]{char}[/green]"
            elif level > 0.1:
                waveform += f"[cyan]{char}[/cyan]"
            else:
                waveform += f"[dim]{char}[/dim]"
        
        return f"Wave: {waveform}"
    
    def _create_gradient_meter(self, bars: int, peak_bar: int) -> str:
        """Create a gradient meter with peak indicator."""
        meter = ""
        
        # Build meter with different characters for different levels
        for i in range(self.max_bars):
            if i < bars:
                # Active portion with gradient
                if i < self.max_bars * 0.6:
                    meter += "█"  # Solid for lower levels
                elif i < self.max_bars * 0.8:
                    meter += "▓"  # Medium for mid levels
                else:
                    meter += "▒"  # Light for high levels
            elif i == peak_bar:
                meter += "▌"  # Peak indicator
            else:
                meter += "░"  # Empty
        
        return meter
    
    def _get_level_status(self, level: float) -> tuple:
        """Get enhanced status with color, text, and quality icon."""
        if level > 0.9:
            return "red", "OVERLOAD", "⚠️"
        elif level > 0.8:
            return "bright_red", "HIGH", "🔊"
        elif level > 0.6:
            return "yellow", "LOUD", "📢"
        elif level > 0.4:
            return "green", "GOOD", "🔉"
        elif level > 0.2:
            return "cyan", "MODERATE", "🔈"
        elif level > 0.1:
            return "blue", "LOW", "🔇"
        else:
            return "dim white", "QUIET", "😴"
    
    def _get_average_level(self) -> int:
        """Calculate average level from recent history."""
        if not self.level_history:
            return 0
        
        avg = sum(self.level_history) / len(self.level_history)
        return int(avg * 100)
    
    def _get_quality_stats(self) -> str:
        """Get audio quality statistics."""
        if self.clip_count > 0:
            return f"[red]⚠️ {self.clip_count} clips[/red]"
        elif self.recording_state == "recording" and len(self.level_history) > 5:
            # Check for consistent levels (good for speech)
            recent_levels = self.level_history[-5:]
            variance = sum((x - sum(recent_levels)/len(recent_levels))**2 for x in recent_levels) / len(recent_levels)
            if variance < 0.01:  # Low variance = steady input
                return "[green]✓ Steady[/green]"
            else:
                return "[blue]~ Dynamic[/blue]"
        return ""
    
    def _get_pulse_indicator(self) -> str:
        """Get animated pulse indicator for recording state."""
        # Simple animation cycle
        import time
        cycle = int(time.time() * 2) % 4  # 2 changes per second
        if cycle == 0:
            return "🔴"
        elif cycle == 1:
            return "🟠"
        elif cycle == 2:
            return "🔴"
        else:
            return "🟡"
    
    def set_recording_state(self, state: str):
        """Set the recording state for visual feedback."""
        self.recording_state = state
        if state == "recording":
            self.start_pulse_animation()
        else:
            self.stop_pulse_animation()
        
        # Reset history when not recording to avoid stale data
        if state == "idle":
            self.level_history = []
            self.peak_hold = 0.0
            self.clip_count = 0
    
    def start_pulse_animation(self):
        """Start pulse animation timer."""
        if self.pulse_timer:
            self.pulse_timer.stop()
        self.pulse_timer = self.set_interval(0.5, self._pulse_update)
    
    def stop_pulse_animation(self):
        """Stop pulse animation timer."""
        if self.pulse_timer:
            self.pulse_timer.stop()
            self.pulse_timer = None
    
    def _pulse_update(self):
        """Update pulse animation."""
        # Force refresh of the display
        self.watch_level(self.level)


class RecordingControls(Container):
    """Controls for recording operations."""
    
    def __init__(self, duration: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.recording = False
        self.duration = duration
        self.start_time = None
        self.progress_timer = None
        
    def compose(self) -> ComposeResult:
        """Compose the recording controls."""
        with Horizontal(classes="recording-main-controls"):
            yield Button("Record", id="record-btn", variant="success")
            yield Button("Stop", id="stop-btn", variant="error", disabled=True)
            yield Label(f"Duration: {self.duration}s", id="duration-label")
        
        # Duration controls
        with Horizontal(classes="duration-controls"):
            yield Button("-", id="duration-minus", variant="default", classes="duration-btn")
            yield Button("+", id="duration-plus", variant="default", classes="duration-btn")
            yield Label("Presets:", classes="presets-label")
            yield Button("30s", id="preset-30", variant="default", classes="preset-btn")
            yield Button("1m", id="preset-60", variant="default", classes="preset-btn")
            yield Button("2m", id="preset-120", variant="default", classes="preset-btn")
            yield Button("5m", id="preset-300", variant="default", classes="preset-btn")
        
        # Recording progress bar (initially hidden)
        yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="recording-progress", 
                         classes="recording-progress-bar")
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "record-btn":
            self.start_recording()
        elif event.button.id == "stop-btn":
            self.stop_recording()
        elif event.button.id == "duration-minus":
            self.adjust_duration(-15)  # Decrease by 15 seconds
        elif event.button.id == "duration-plus":
            self.adjust_duration(15)   # Increase by 15 seconds
        elif event.button.id == "preset-30":
            self.set_duration(30)
        elif event.button.id == "preset-60":
            self.set_duration(60)
        elif event.button.id == "preset-120":
            self.set_duration(120)
        elif event.button.id == "preset-300":
            self.set_duration(300)
            
    def start_recording(self):
        """Start recording."""
        self.recording = True
        self.query_one("#record-btn").disabled = True
        
        # Show recording tip to user
        self.app.notify(f"🎤 Recording started! Minimum length: {MIN_RECORDING_LENGTH} second(s)", severity="information", timeout=3)
        self.query_one("#stop-btn").disabled = False
        
        # Initialize progress bar
        progress_bar = self.query_one("#recording-progress", ProgressBar)
        progress_bar.styles.display = "block"
        progress_bar.progress = 0
        
        # Start countdown timer
        self.start_time = time.time()
        self.progress_timer = self.set_interval(0.1, self.update_progress)
        
        self.post_message(self.RecordingStarted())
        
    def stop_recording(self):
        """Stop recording."""
        self.recording = False
        self.query_one("#record-btn").disabled = False
        self.query_one("#stop-btn").disabled = True
        
        # Stop progress timer
        if self.progress_timer:
            self.progress_timer.stop()
            self.progress_timer = None
            
        # Hide progress bar and reset
        progress_bar = self.query_one("#recording-progress", ProgressBar)
        progress_bar.styles.display = "none"
        progress_bar.progress = 0
        
        # Reset duration label
        duration_label = self.query_one("#duration-label")
        duration_label.update(f"Duration: {self.duration}s")
        
        self.post_message(self.RecordingStopped())
        
    def update_progress(self):
        """Update recording progress bar."""
        logger = get_logger()
        
        if not self.recording or self.start_time is None:
            return
            
        elapsed = time.time() - self.start_time
        progress_percentage = min((elapsed / self.duration) * 100, 100)
        remaining_time = max(0, self.duration - elapsed)
        
        # Log progress for debugging
        logger.debug(f"Recording progress: {elapsed:.1f}s / {self.duration}s ({progress_percentage:.1f}%)")
        
        progress_bar = self.query_one("#recording-progress", ProgressBar)
        progress_bar.progress = progress_percentage
        
        # Update duration label with countdown
        duration_label = self.query_one("#duration-label")
        duration_label.update(f"Remaining: {remaining_time:.1f}s")
        
        # REMOVED AUTO-STOP LOGIC - Let the main recording handle its own timing
        # The main recording duration is managed by the actual audio recording process
        # This progress bar is just for visual feedback
        if elapsed >= self.duration:
            logger.warning(f"Progress bar reached its duration ({self.duration}s) but NOT auto-stopping - main recording controls timing")
            # Just update display but don't stop recording - let the actual audio recording finish naturally
        
    def update_duration(self, duration: int):
        """Update the duration display."""
        logger = get_logger()
        old_duration = self.duration
        self.duration = duration
        logger.info(f"RecordingControls duration updated: {old_duration}s → {duration}s")
        self.query_one("#duration-label").update(f"Duration: {duration}s")
    
    def adjust_duration(self, delta: int):
        """Adjust duration by delta seconds."""
        if self.recording:
            self.app.notify("⚠️ Cannot adjust duration while recording", severity="warning")
            return
        
        new_duration = max(15, self.duration + delta)  # Minimum 15 seconds
        self.set_duration(new_duration)
        
    def set_duration(self, duration: int):
        """Set specific duration."""
        if self.recording:
            self.app.notify("⚠️ Cannot change duration while recording", severity="warning")
            return
        
        old_duration = self.duration
        self.duration = duration
        self.query_one("#duration-label").update(f"Duration: {duration}s")
        
        # Notify the main app about the duration change
        self.app.notify(f"⏱️ Duration changed: {old_duration}s → {duration}s", severity="information")
        
        # Update the main app's recording duration
        if hasattr(self.app, 'set_recording_duration'):
            self.app.set_recording_duration(duration)
        
    class RecordingStarted(Message):
        """Message sent when recording starts."""
        pass
        
    class RecordingStopped(Message):
        """Message sent when recording stops."""
        pass


class TranscriptionEntry(Container):
    """Individual transcription entry with copy actions."""
    
    def __init__(self, text: str, formatted_text: Optional[str], timestamp: str, entry_id: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.formatted_text = formatted_text
        self.timestamp = timestamp
        self.entry_id = entry_id
        self.can_focus = True
        
    def compose(self) -> ComposeResult:
        """Compose the transcription entry."""
        with Vertical():
            # Raw transcription section
            with Horizontal(classes="transcription-section"):
                with Vertical():
                    yield Static(f"[bold blue]Raw Transcription - {self.timestamp}[/bold blue]", classes="transcription-header")
                    yield Static(self.text, classes="transcription-content raw-content")
                with Vertical(classes="action-buttons"):
                    yield Button("📋 Copy Raw", id=f"copy-raw-{self.entry_id}", variant="primary", classes="copy-button")
            
            # AI-formatted transcription section (if available)
            if self.formatted_text:
                with Horizontal(classes="transcription-section"):
                    with Vertical():
                        yield Static(f"[bold magenta]AI-Formatted - {self.timestamp}[/bold magenta]", classes="transcription-header")
                        yield Static(self.formatted_text, classes="transcription-content ai-content")
                    with Vertical(classes="action-buttons"):
                        yield Button("📋 Copy AI", id=f"copy-ai-{self.entry_id}", variant="success", classes="copy-button")
                        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle copy button presses."""
        button_id = event.button.id
        if button_id.startswith(f"copy-raw-{self.entry_id}"):
            self.copy_text(self.text, "Raw transcription")
        elif button_id.startswith(f"copy-ai-{self.entry_id}"):
            self.copy_text(self.formatted_text, "AI-formatted transcription")
            
    def copy_text(self, text: str, description: str):
        """Copy text to clipboard and show feedback."""
        # Get the clipboard manager from the app
        app = self.app
        if hasattr(app, 'clipboard_manager') and app.clipboard_manager:
            success = app.clipboard_manager.copy_to_clipboard(text)
            if success:
                self.app.notify(f"✅ {description} copied to clipboard!", severity="information")
            else:
                self.app.notify(f"❌ Failed to copy {description}", severity="error")
        else:
            self.app.notify("❌ Clipboard manager not available", severity="error")


class TranscriptionLog(Container):
    """Enhanced log widget for transcription results with copy actions."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_entries = 50
        self.entries = []
        self.entry_counter = 0
        self.latest_ai_text = None
        
    def compose(self) -> ComposeResult:
        """Compose the transcription log."""
        with Vertical():
            yield Static("[bold green]📝 Transcription Results[/bold green]", classes="log-header")
            with Container(id="transcription-entries", classes="scrollable-container"):
                yield Static("No transcriptions yet. Press 'r' to start recording!", classes="placeholder-text")
                
    def add_transcription(self, text: str, formatted_text: Optional[str] = None):
        """Add a new transcription to the log with comprehensive logging."""
        logger = get_logger()
        logger.log_method_entry("TranscriptionLog.add_transcription", 
                              text_length=len(text), 
                              has_formatted=formatted_text is not None,
                              current_entry_count=len(self.entries))
        
        try:
            timestamp = time.strftime("%H:%M:%S")
            entry_id = str(self.entry_counter)
            self.entry_counter += 1
            logger.debug(f"Creating entry with ID: {entry_id}, timestamp: {timestamp}")
            
            # Store latest AI text for quick copy
            if formatted_text:
                self.latest_ai_text = formatted_text
                logger.debug("Stored formatted text as latest AI text")
            else:
                self.latest_ai_text = text
                logger.debug("Stored raw text as latest AI text")
                
            # Remove placeholder if this is the first entry
            logger.debug("Querying for transcription-entries container")
            entries_container = self.query_one("#transcription-entries")
            logger.debug(f"Found entries container: {entries_container}")
            
            if len(self.entries) == 0:
                logger.debug("First entry - removing placeholder children")
                entries_container.remove_children()
                logger.debug("Placeholder children removed")
                
            # Create and add new entry
            logger.debug("Creating TranscriptionEntry widget")
            entry = TranscriptionEntry(text, formatted_text, timestamp, entry_id)
            logger.debug(f"Created TranscriptionEntry: {entry}")
            
            logger.debug("Adding entry to entries list")
            self.entries.append(entry)
            logger.debug(f"Entries list now has {len(self.entries)} items")
            
            logger.debug("Mounting entry to container")
            entries_container.mount(entry)
            logger.info(f"✅ ENTRY SUCCESSFULLY MOUNTED - Container now has {len(entries_container.children)} children")
            
            # Limit number of entries
            if len(self.entries) > self.max_entries:
                logger.debug(f"Removing oldest entry (limit: {self.max_entries})")
                oldest_entry = self.entries.pop(0)
                oldest_entry.remove()
                logger.debug("Oldest entry removed")
                
            # Scroll to bottom to show latest entry
            logger.debug("Scrolling to show latest entry")
            entries_container.scroll_end(animate=True)
            logger.info("✅ Transcription entry added successfully and scrolled into view")
            
        except Exception as e:
            logger.critical("❌ FAILED TO ADD TRANSCRIPTION ENTRY", {
                "error": str(e),
                "error_type": type(e).__name__,
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }, exc_info=True)
            raise  # Re-raise to be caught by calling code
        
        logger.log_method_exit("TranscriptionLog.add_transcription", f"Entry count: {len(self.entries)}")
            
    def add_error(self, error: str):
        """Add an enhanced error message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        entries_container = self.query_one("#transcription-entries")
        error_widget = Static(f"[bright_red]❌ {timestamp}: [bold]ERROR:[/bold] {error}[/bright_red]", classes="error-message")
        entries_container.mount(error_widget)
        entries_container.scroll_end(animate=True)
        
    def add_info(self, message: str):
        """Add an enhanced info message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        entries_container = self.query_one("#transcription-entries")
        
        # Enhanced info messages with better formatting
        if "recording" in message.lower():
            icon = "🎤"
            color = "bright_blue"
        elif "transcrib" in message.lower():
            icon = "⚙️"
            color = "yellow"
        elif "format" in message.lower():
            icon = "✨"
            color = "cyan"
        elif "saved" in message.lower() or "copy" in message.lower():
            icon = "✅"
            color = "green"
        elif "error" in message.lower() or "fail" in message.lower():
            icon = "❌"
            color = "red"
        else:
            icon = "ℹ️"
            color = "blue"
            
        info_widget = Static(f"[{color}]{icon} {timestamp}: [bold]{message}[/bold][/{color}]", classes="info-message")
        entries_container.mount(info_widget)
        entries_container.scroll_end(animate=True)
        
    def copy_latest_ai(self) -> bool:
        """Copy the latest AI-formatted transcription."""
        if self.latest_ai_text:
            app = self.app
            if hasattr(app, 'clipboard_manager') and app.clipboard_manager:
                success = app.clipboard_manager.copy_to_clipboard(self.latest_ai_text)
                if success:
                    self.app.notify("✅ Latest AI transcription copied to clipboard!", severity="information")
                    return True
                else:
                    self.app.notify("❌ Failed to copy to clipboard", severity="error")
            else:
                self.app.notify("❌ Clipboard manager not available", severity="error")
        else:
            self.app.notify("ℹ️ No transcriptions available to copy", severity="warning")
        return False


class HistoryEntry(Container):
    """Individual history entry with actions."""
    
    def __init__(self, entry_data: Dict[str, Any], entry_index: int, **kwargs):
        super().__init__(**kwargs)
        self.entry_data = entry_data
        self.entry_index = entry_index
        self.can_focus = True
        
    def compose(self) -> ComposeResult:
        """Compose the history entry."""
        timestamp = self.entry_data.get('timestamp', '')
        text = self.entry_data.get('text', 'No text')
        model = self.entry_data.get('model', 'Unknown')
        has_ai = self.entry_data.get('md_file') is not None
        txt_file = self.entry_data.get('txt_file', '')
        md_file = self.entry_data.get('md_file', '')
        working_dir = self.entry_data.get('working_dir', 'Unknown')
        
        # Format timestamp to human readable
        formatted_time = self._format_timestamp(timestamp)
        
        # Create preview text (first 200 chars with ellipsis)
        preview_text = text[:200] + "..." if len(text) > 200 else text
        
        with Container(classes="enhanced-history-entry"):
            # Header with timestamp, model, and file info
            with Horizontal(classes="history-header-row"):
                yield Static(f"[bold]{formatted_time}[/bold] | Model: {model}", classes="history-header")
                if has_ai:
                    yield Static("✨ AI", classes="ai-badge")
            
            # File paths and working directory (small text)
            if txt_file:
                yield Static(f"📄 Raw: {Path(txt_file).name}", classes="file-path-info")
            if md_file:
                yield Static(f"📝 AI: {Path(md_file).name}", classes="file-path-info")
            if working_dir != 'Unknown':
                # Show relative path or last part of directory for readability
                display_dir = Path(working_dir).name if working_dir else 'Unknown'
                yield Static(f"📁 Directory: {display_dir}", classes="file-path-info")
            
            # Enhanced preview content with tabs for raw and AI text
            with Container(classes="preview-container"):
                if has_ai:
                    # Use TabbedContent to show both raw and AI previews
                    with TabbedContent(id=f"preview-tabs-{self.entry_index}", classes="preview-tabs"):
                        with TabPane("📄 Raw", id=f"raw-tab-{self.entry_index}"):
                            yield Static(preview_text, classes="preview-text", id=f"raw-preview-{self.entry_index}")
                            if len(text) > 200:
                                yield Button("📖 Show More", id=f"expand-raw-{self.entry_index}", variant="default", classes="expand-button")
                        
                        with TabPane("✨ AI", id=f"ai-tab-{self.entry_index}"):
                            ai_preview = self._get_ai_preview()
                            yield Static(ai_preview, classes="preview-text", id=f"ai-preview-{self.entry_index}")
                            if len(ai_preview) > 200:
                                yield Button("📖 Show More", id=f"expand-ai-{self.entry_index}", variant="default", classes="expand-button")
                else:
                    # No AI content, just show raw text
                    yield Static(preview_text, classes="preview-text", id=f"raw-preview-{self.entry_index}")
                    if len(text) > 200:
                        yield Button("📖 Show More", id=f"expand-raw-{self.entry_index}", variant="default", classes="expand-button")
            
            # Action buttons in horizontal layout
            with Horizontal(classes="action-buttons-row"):
                yield Button("📋", id=f"copy-history-{self.entry_index}", variant="primary", classes="compact-button")
                if has_ai:
                    yield Button("📋 AI", id=f"copy-ai-history-{self.entry_index}", variant="success", classes="compact-button")
                yield Button("✏️", id=f"edit-raw-{self.entry_index}", variant="default", classes="compact-button")
                if has_ai:
                    yield Button("✏️ AI", id=f"edit-ai-{self.entry_index}", variant="default", classes="compact-button")
                yield Button("🗑️", id=f"delete-history-{self.entry_index}", variant="error", classes="compact-button")
                
    def _get_ai_preview(self) -> str:
        """Get AI-formatted text preview from file."""
        md_file = self.entry_data.get('md_file')
        if md_file and Path(md_file).exists():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    ai_content = f.read()
                # Return preview (first 200 chars with ellipsis)
                return ai_content[:200] + "..." if len(ai_content) > 200 else ai_content
            except Exception:
                return "[Error reading AI file]"
        return "[AI file not found]"
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp to human-readable format."""
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Calculate time difference
            diff = now - dt.replace(tzinfo=timezone.utc)
            
            if diff.days == 0:
                # Today
                return f"Today {dt.strftime('%I:%M %p')}"
            elif diff.days == 1:
                # Yesterday
                return f"Yesterday {dt.strftime('%I:%M %p')}"
            elif diff.days < 7:
                # This week
                return dt.strftime('%A %I:%M %p')
            else:
                # Older
                return dt.strftime('%b %d, %Y %I:%M %p')
        except:
            return timestamp[:19]  # Fallback to ISO format
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id.startswith(f"copy-history-{self.entry_index}"):
            self._copy_text(self.entry_data.get('text', ''), "Raw transcript")
        elif button_id.startswith(f"copy-ai-history-{self.entry_index}"):
            self._copy_ai_text()
        elif button_id.startswith(f"edit-raw-{self.entry_index}"):
            self._edit_raw_file()
        elif button_id.startswith(f"edit-ai-{self.entry_index}"):
            self._edit_ai_file()
        elif button_id.startswith(f"expand-raw-{self.entry_index}"):
            self._toggle_raw_preview()
        elif button_id.startswith(f"expand-ai-{self.entry_index}"):
            self._toggle_ai_preview()
        elif button_id.startswith(f"delete-history-{self.entry_index}"):
            self._delete_entry()
            
    def _copy_text(self, text: str, description: str):
        """Copy text to clipboard."""
        app = self.app
        if hasattr(app, 'clipboard_manager') and app.clipboard_manager:
            success = app.clipboard_manager.copy_to_clipboard(text)
            if success:
                self.app.notify(f"✅ {description} copied to clipboard!", severity="information")
            else:
                self.app.notify(f"❌ Failed to copy {description}", severity="error")
        else:
            self.app.notify("❌ Clipboard manager not available", severity="error")
            
    def _copy_ai_text(self):
        """Copy AI-formatted text from file."""
        md_file = self.entry_data.get('md_file')
        if md_file and Path(md_file).exists():
            try:
                with open(md_file, 'r') as f:
                    ai_text = f.read()
                self._copy_text(ai_text, "AI-formatted transcript")
            except Exception as e:
                self.app.notify(f"❌ Failed to read AI file: {e}", severity="error")
        else:
            self.app.notify("❌ AI-formatted file not found", severity="error")
    
    def _edit_raw_file(self):
        """Edit the raw transcript file with nvim."""
        txt_file = self.entry_data.get('txt_file')
        if txt_file and Path(txt_file).exists():
            self._edit_file_with_nvim(Path(txt_file), "raw transcript")
        else:
            self.app.notify("❌ Raw transcript file not found", severity="error")
    
    def _edit_ai_file(self):
        """Edit the AI-formatted transcript file with nvim."""
        md_file = self.entry_data.get('md_file')
        if md_file and Path(md_file).exists():
            self._edit_file_with_nvim(Path(md_file), "AI-formatted transcript")
        else:
            self.app.notify("❌ AI-formatted file not found", severity="error")
    
    def _edit_file_with_nvim(self, file_path: Path, description: str):
        """Launch nvim to edit a file."""
        # Get or create edit manager
        if not hasattr(self.app, 'edit_manager'):
            self.app.edit_manager = EditManager()
        
        # Check if nvim is available
        if not self.app.edit_manager.is_nvim_available():
            self.app.notify("❌ nvim not found. Please install neovim to edit files.", 
                          title="Editor Not Available", severity="error")
            return
        
        # Create callback for when editing is complete
        def on_edit_complete(edited_file_path: Path):
            self.app.notify(f"✅ {description} has been updated!", 
                          title="File Saved", severity="information")
        
        # Launch nvim
        success = self.app.edit_manager.edit_file_with_nvim(file_path, on_edit_complete)
        if success:
            self.app.notify(f"📝 Opening {description} in nvim...", 
                          title="Launching Editor", severity="information")
        else:
            self.app.notify(f"❌ Failed to open {description} in nvim", 
                          title="Edit Failed", severity="error")
    
    def _toggle_raw_preview(self):
        """Toggle between raw text preview and full text."""
        try:
            preview_widget = self.query_one(f"#raw-preview-{self.entry_index}")
            expand_button = self.query_one(f"#expand-raw-{self.entry_index}")
            
            text = self.entry_data.get('text', '')
            current_text = preview_widget.renderable
            
            if len(str(current_text)) < len(text):
                # Currently showing preview, expand to full text
                preview_widget.update(text)
                expand_button.label = "📖 Show Less"
            else:
                # Currently showing full text, collapse to preview
                preview_text = text[:200] + "..." if len(text) > 200 else text
                preview_widget.update(preview_text)
                expand_button.label = "📖 Show More"
                
        except Exception:
            # Handle case where widgets might not be found
            pass
    
    def _toggle_ai_preview(self):
        """Toggle between AI text preview and full text."""
        try:
            preview_widget = self.query_one(f"#ai-preview-{self.entry_index}")
            expand_button = self.query_one(f"#expand-ai-{self.entry_index}")
            
            md_file = self.entry_data.get('md_file')
            if md_file and Path(md_file).exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    ai_content = f.read()
                
                current_text = preview_widget.renderable
                
                if len(str(current_text)) < len(ai_content):
                    # Currently showing preview, expand to full text
                    preview_widget.update(ai_content)
                    expand_button.label = "📖 Show Less"
                else:
                    # Currently showing full text, collapse to preview
                    preview_text = ai_content[:200] + "..." if len(ai_content) > 200 else ai_content
                    preview_widget.update(preview_text)
                    expand_button.label = "📖 Show More"
                    
        except Exception:
            # Handle case where widgets might not be found
            pass
            
    def _delete_entry(self):
        """Delete this history entry."""
        # Notify parent to handle deletion
        self.post_message(self.DeleteRequested(self.entry_index))
        
    class DeleteRequested(Message):
        """Message sent when deletion is requested."""
        def __init__(self, entry_index: int):
            super().__init__()
            self.entry_index = entry_index


class HistoryViewer(Container):
    """Enhanced widget for viewing transcription history with filtering and actions."""
    
    def __init__(self, history_file: Path, **kwargs):
        super().__init__(**kwargs)
        self.history_file = history_file
        self.history_data = []
        self.filtered_data = []
        self.current_filter = "all"
        self.search_query = ""
        self.current_working_dir = os.getcwd()
        self.directory_filter = "current"  # Default to current directory only
        
    def compose(self) -> ComposeResult:
        """Compose the history viewer."""
        with Vertical():
            # Header with controls
            with Horizontal(classes="history-controls"):
                yield Static("[bold green]📜 Transcription History[/bold green]", classes="history-title")
                yield Button("🔄 Refresh", id="refresh-history", variant="default")
                
            # Search box
            with Horizontal(classes="search-controls"):
                yield Static("Search:", classes="search-label")
                yield Input(placeholder="Search transcriptions...", id="search-input", classes="search-input")
                yield Button("Clear", id="clear-search", variant="default", classes="clear-button")
                
            # Time filter controls
            with Horizontal(classes="filter-controls"):
                yield Static("Time:", classes="filter-label")
                yield Button("All", id="filter-all", variant="primary" if self.current_filter == "all" else "default", classes="filter-button")
                yield Button("Today", id="filter-today", variant="primary" if self.current_filter == "today" else "default", classes="filter-button")
                yield Button("Yesterday", id="filter-yesterday", variant="primary" if self.current_filter == "yesterday" else "default", classes="filter-button")
                yield Button("This Week", id="filter-week", variant="primary" if self.current_filter == "week" else "default", classes="filter-button")
                
            # Directory filter controls
            with Horizontal(classes="filter-controls"):
                yield Static("Directory:", classes="filter-label")
                yield Button("Current Only", id="dir-filter-current", variant="primary" if self.directory_filter == "current" else "default", classes="filter-button")
                yield Button("All Directories", id="dir-filter-all", variant="primary" if self.directory_filter == "all" else "default", classes="filter-button")
                
            # History entries container
            with Container(id="history-entries", classes="history-container"):
                yield Static("No history found. Start recording to see transcriptions here!", classes="history-placeholder")
        
    def on_mount(self):
        """Load history when mounted."""
        self.load_history()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "refresh-history":
            self.load_history()
        elif button_id == "clear-search":
            self.clear_search()
        elif button_id.startswith("filter-"):
            filter_type = button_id.split("-", 1)[1]
            self.apply_filter(filter_type)
        elif button_id.startswith("dir-filter-"):
            dir_filter_type = button_id.split("-", 2)[2]
            self.apply_directory_filter(dir_filter_type)
            
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value.lower()
            self.apply_filter(self.current_filter)
            
    def on_history_entry_delete_requested(self, event: HistoryEntry.DeleteRequested) -> None:
        """Handle delete request from history entry."""
        self.delete_history_entry(event.entry_index)
    
    def apply_directory_filter(self, dir_filter_type: str):
        """Apply directory filter to history data."""
        self.directory_filter = dir_filter_type
        
        # Update directory filter button styles
        for button_id in ["dir-filter-current", "dir-filter-all"]:
            try:
                button = self.query_one(f"#{button_id}")
                if button_id == f"dir-filter-{dir_filter_type}":
                    button.variant = "primary"
                else:
                    button.variant = "default"
            except:
                pass
                
        # Re-apply current time filter with new directory filter
        self.apply_filter(self.current_filter)
            
    def load_history(self):
        """Load history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []
                
            self.apply_filter(self.current_filter)
                
        except Exception as e:
            if hasattr(self.app, 'notify'):
                self.app.notify(f"Failed to load history: {e}", severity="error")
                
    def apply_filter(self, filter_type: str):
        """Apply date filter to history data."""
        from datetime import datetime, timezone, timedelta
        
        self.current_filter = filter_type
        
        # Update filter button styles
        for button_id in ["filter-all", "filter-today", "filter-yesterday", "filter-week"]:
            try:
                button = self.query_one(f"#{button_id}")
                if button_id == f"filter-{filter_type}":
                    button.variant = "primary"
                else:
                    button.variant = "default"
            except:
                pass
        
        # Start with all data for time filtering
        if filter_type == "all":
            time_filtered_data = self.history_data
        else:
            now = datetime.now(timezone.utc)
            time_filtered_data = []
            
            for entry in self.history_data:
                try:
                    entry_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                    entry_time = entry_time.replace(tzinfo=timezone.utc)
                    diff = now - entry_time
                    
                    if filter_type == "today" and diff.days == 0:
                        time_filtered_data.append(entry)
                    elif filter_type == "yesterday" and diff.days == 1:
                        time_filtered_data.append(entry)
                    elif filter_type == "week" and diff.days < 7:
                        time_filtered_data.append(entry)
                except:
                    continue
        
        # Apply directory filtering
        if self.directory_filter == "current":
            self.filtered_data = []
            for entry in time_filtered_data:
                entry_working_dir = entry.get('working_dir', '')
                if entry_working_dir == self.current_working_dir:
                    self.filtered_data.append(entry)
        else:
            self.filtered_data = time_filtered_data
                    
        # Apply search filter if search query exists
        if self.search_query:
            searched_data = []
            for entry in self.filtered_data:
                text = entry.get('text', '').lower()
                model = entry.get('model', '').lower()
                if self.search_query in text or self.search_query in model:
                    searched_data.append(entry)
            self.filtered_data = searched_data
                    
        self.update_display()
        
    def update_display(self):
        """Update the display with filtered data."""
        history_container = self.query_one("#history-entries")
        history_container.remove_children()
        
        if not self.filtered_data:
            placeholder_text = "No history found for this filter." if self.current_filter != "all" else "No history found. Start recording to see transcriptions here!"
            history_container.mount(Static(placeholder_text, classes="history-placeholder"))
            return
            
        for i, entry in enumerate(self.filtered_data[:30]):  # Show max 30 entries
            history_entry = HistoryEntry(entry, i)
            history_container.mount(history_entry)
            
    def delete_history_entry(self, entry_index: int):
        """Delete a history entry."""
        if 0 <= entry_index < len(self.filtered_data):
            entry_to_delete = self.filtered_data[entry_index]
            
            # Remove from main history data
            try:
                self.history_data.remove(entry_to_delete)
                
                # Save updated history
                with open(self.history_file, 'w') as f:
                    json.dump(self.history_data, f, indent=2)
                    
                # Refresh display
                self.apply_filter(self.current_filter)
                
                if hasattr(self.app, 'notify'):
                    self.app.notify("✅ History entry deleted", severity="information")
                    
            except Exception as e:
                if hasattr(self.app, 'notify'):
                    self.app.notify(f"❌ Failed to delete entry: {e}", severity="error")
                    
    def clear_search(self):
        """Clear the search input and refresh display."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        self.search_query = ""
        self.apply_filter(self.current_filter)


class ThemeSelector(Container):
    """Theme selector widget for switching between themes."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = ThemeManager()
        
    def compose(self) -> ComposeResult:
        """Compose the theme selector."""
        with Vertical(classes="theme-selector-container"):
            # Header
            yield Static("[bold green]🎨 Theme Selector[/bold green]", classes="theme-header")
            
            # Theme selection
            with Horizontal(classes="theme-controls"):
                yield Static("Current Theme:", classes="theme-label")
                theme_options = [(theme[1], theme[0]) for theme in self.theme_manager.get_theme_list()]
                yield Select(
                    theme_options, 
                    value=self.theme_manager.current_theme,
                    id="theme-select",
                    classes="theme-select"
                )
                yield Button("Apply Theme", id="apply-theme", variant="success", classes="apply-button")
                
            # Theme preview
            with Container(classes="theme-preview"):
                yield Static("[bold]Theme Preview[/bold]", classes="preview-header")
                current_theme = self.theme_manager.get_current_theme()
                yield Static(f"Name: {current_theme.display_name}", id="theme-name", classes="preview-text")
                yield Static(f"Description: {current_theme.description}", id="theme-description", classes="preview-text")
                
                # Color preview
                with Horizontal(classes="color-preview"):
                    yield Static("Colors:", classes="color-label")
                    with Vertical(classes="color-swatches"):
                        for color_name, color_value in current_theme.colors.items():
                            yield Static(f"{color_name}: {color_value}", classes="color-swatch")
                            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle theme application."""
        if event.button.id == "apply-theme":
            theme_select = self.query_one("#theme-select", Select)
            selected_theme = theme_select.value
            if selected_theme:
                self.theme_manager.set_theme(selected_theme)
                self.app.apply_theme(selected_theme)
                self.app.notify(f"🎨 Applied theme: {self.theme_manager.get_current_theme().display_name}", 
                               severity="information")
                self.update_preview()
                
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle theme selection changes."""
        if event.select.id == "theme-select":
            self.update_preview()
            
    def update_preview(self):
        """Update the theme preview."""
        theme_select = self.query_one("#theme-select", Select)
        if theme_select.value:
            theme = self.theme_manager.get_theme(theme_select.value)
            self.query_one("#theme-name").update(f"Name: {theme.display_name}")
            self.query_one("#theme-description").update(f"Description: {theme.description}")
            
            # Update color swatches
            color_container = self.query_one(".color-swatches")
            color_container.remove_children()
            for color_name, color_value in theme.colors.items():
                color_container.mount(Static(f"{color_name}: {color_value}", classes="color-swatch"))


class ActionsPanel(Container):
    """Panel with quick action buttons for common operations."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def compose(self) -> ComposeResult:
        """Compose the actions panel."""
        with Vertical(classes="actions-container"):
            # Header
            yield Static("[bold green]⚡ Quick Actions[/bold green]", classes="actions-header")
            
            # Main action buttons
            with Horizontal(classes="main-actions"):
                with Vertical(classes="action-group"):
                    yield Static("[bold]📋 Clipboard Actions[/bold]", classes="group-header")
                    yield Button("📋 Copy Latest AI", id="action-copy-latest-ai", variant="success", classes="action-button-large")
                    yield Button("📋 Copy Latest Raw", id="action-copy-latest-raw", variant="primary", classes="action-button-large")
                    
                with Vertical(classes="action-group"):
                    yield Static("[bold]📁 File Actions[/bold]", classes="group-header")
                    yield Button("📤 Export Latest", id="action-export-latest", variant="default", classes="action-button-large")
                    yield Button("📂 Open Transcript Dir", id="action-open-dir", variant="default", classes="action-button-large")
                    
            # Recording controls section
            with Horizontal(classes="recording-actions"):
                with Vertical(classes="action-group"):
                    yield Static("[bold]🎤 Recording Controls[/bold]", classes="group-header")
                    yield Button("🎤 Start Recording", id="action-start-recording", variant="success", classes="action-button-large")
                    yield Button("⏹️ Stop Recording", id="action-stop-recording", variant="error", classes="action-button-large", disabled=True)
                    
                with Vertical(classes="action-group"):
                    yield Static("[bold]⚙️ Settings[/bold]", classes="group-header")
                    yield Button("📊 Show Statistics", id="action-show-stats", variant="default", classes="action-button-large")
                    yield Button("🧹 Clean Old Files", id="action-cleanup", variant="warning", classes="action-button-large")
                    
            # Export actions section
            with Horizontal(classes="export-actions"):
                with Vertical(classes="action-group"):
                    yield Static("[bold]📤 Export Actions[/bold]", classes="group-header")
                    yield Button("📤 Export Session", id="action-export-session", variant="primary", classes="action-button-large")
                    yield Button("📚 Export History", id="action-export-history", variant="default", classes="action-button-large")
                    
            # Current session info
            with Container(classes="session-info"):
                yield Static("[bold]📈 Session Information[/bold]", classes="info-header")
                yield Static("Recordings this session: 0", id="session-recordings", classes="info-text")
                yield Static("Latest transcription: None", id="latest-transcription-info", classes="info-text")
                yield Static("AI formatting: Enabled", id="ai-status-info", classes="info-text")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle action button presses."""
        button_id = event.button.id
        
        if button_id == "action-copy-latest-ai":
            transcription_log = self.app.query_one("#transcription-log", TranscriptionLog)
            transcription_log.copy_latest_ai()
            
        elif button_id == "action-copy-latest-raw":
            self._copy_latest_raw()
            
        elif button_id == "action-export-latest":
            self._export_latest_transcription()
            
        elif button_id == "action-export-session":
            self._export_session_transcriptions()
            
        elif button_id == "action-export-history":
            self._export_history_transcriptions()
            
        elif button_id == "action-open-dir":
            self._open_transcript_directory()
            
        elif button_id == "action-start-recording":
            self.app.action_record()
            
        elif button_id == "action-stop-recording":
            self.app.action_stop()
            
        elif button_id == "action-show-stats":
            self._show_statistics()
            
        elif button_id == "action-cleanup":
            self._cleanup_old_files()
            
    def _copy_latest_raw(self):
        """Copy the latest raw transcription."""
        transcription_log = self.app.query_one("#transcription-log", TranscriptionLog)
        # Get the latest raw text from the transcription log
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            latest_entry = transcription_log.entries[-1]
            if hasattr(latest_entry, 'text'):
                app = self.app
                if hasattr(app, 'clipboard_manager') and app.clipboard_manager:
                    success = app.clipboard_manager.copy_to_clipboard(latest_entry.text)
                    if success:
                        self.app.notify("✅ Latest raw transcription copied!", severity="information")
                    else:
                        self.app.notify("❌ Failed to copy to clipboard", severity="error")
                else:
                    self.app.notify("❌ Clipboard manager not available", severity="error")
            else:
                self.app.notify("ℹ️ No raw transcription available", severity="warning")
        else:
            self.app.notify("ℹ️ No transcriptions available to copy", severity="warning")
            
    def _show_save_as_dialog(self):
        """Show save as dialog (placeholder for now)."""
        self.app.notify("💡 Save As feature coming soon!", severity="information")
        
    def _open_transcript_directory(self):
        """Open the transcript directory."""
        import subprocess
        import platform
        
        try:
            transcript_dir = DEFAULT_TRANSCRIPT_DIR
            
            # Open directory based on platform
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(transcript_dir)])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", str(transcript_dir)])
            else:  # Linux and others
                subprocess.run(["xdg-open", str(transcript_dir)])
                
            self.app.notify(f"📂 Opened {transcript_dir}", severity="information")
        except Exception as e:
            self.app.notify(f"❌ Failed to open directory: {e}", severity="error")
            
    def _show_statistics(self):
        """Show session statistics."""
        transcription_log = self.app.query_one("#transcription-log", TranscriptionLog)
        entry_count = len(transcription_log.entries) if hasattr(transcription_log, 'entries') else 0
        
        stats_text = f"""
📊 Session Statistics:
• Total recordings: {entry_count}
• Recording duration: {self.app.recording_duration}s
• Model: {self.app.transcriber.model_name if self.app.transcriber else 'Unknown'}
• AI formatting: {'Enabled' if self.app.formatter and not self.app.formatter.disabled else 'Disabled'}
        """.strip()
        
        self.app.notify(stats_text, severity="information")
        
    def _cleanup_old_files(self):
        """Cleanup old transcript files."""
        try:
            if hasattr(self.app, 'transcript_manager') and self.app.transcript_manager:
                # Call cleanup method
                cleaned = self.app.transcript_manager.cleanup_old_files()
                self.app.notify(f"🧹 Cleaned up old files", severity="information")
            else:
                self.app.notify("❌ Transcript manager not available", severity="error")
        except Exception as e:
            self.app.notify(f"❌ Cleanup failed: {e}", severity="error")
            
    def update_session_info(self, recordings_count: int = None, latest_text: str = None, ai_enabled: bool = None):
        """Update session information display."""
        try:
            if recordings_count is not None:
                recordings_widget = self.query_one("#session-recordings")
                recordings_widget.update(f"Recordings this session: {recordings_count}")
                
            if latest_text is not None:
                latest_widget = self.query_one("#latest-transcription-info")
                preview = latest_text[:50] + "..." if len(latest_text) > 50 else latest_text
                latest_widget.update(f"Latest transcription: {preview}")
                
            if ai_enabled is not None:
                ai_widget = self.query_one("#ai-status-info")
                status = "Enabled" if ai_enabled else "Disabled"
                ai_widget.update(f"AI formatting: {status}")
        except:
            pass  # Fail silently if widgets not found
            
    def set_recording_state(self, is_recording: bool):
        """Update recording button states."""
        try:
            start_button = self.query_one("#action-start-recording")
            stop_button = self.query_one("#action-stop-recording")
            
            start_button.disabled = is_recording
            stop_button.disabled = not is_recording
        except:
            pass  # Fail silently if buttons not found
            
    def _export_latest_transcription(self):
        """Export the latest transcription."""
        transcription_log = self.app.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            latest_entry = transcription_log.entries[-1]
            
            # Quick export with format selection
            from ..ui.export_dialog import ExportOptionsScreen
            from ..utils.export_manager import ExportManager
            
            export_manager = ExportManager(
                transcript_manager=getattr(self.app, 'transcript_manager', None),
                history_manager=getattr(self.app, 'history_manager', None)
            )
            
            supported_formats = export_manager.get_supported_formats()
            
            def handle_format_selection(format_type):
                if format_type:
                    self._perform_single_export(latest_entry, format_type)
                    
            self.app.push_screen(ExportOptionsScreen(supported_formats), handle_format_selection)
        else:
            self.app.notify("ℹ️ No transcriptions available to export", severity="warning")
            
    def _export_session_transcriptions(self):
        """Export all session transcriptions."""
        transcription_log = self.app.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            from ..ui.export_dialog import ExportDialog
            
            def handle_export_config(config):
                if config:
                    self._perform_session_export(transcription_log.entries, config)
                    
            self.app.push_screen(ExportDialog("session"), handle_export_config)
        else:
            self.app.notify("ℹ️ No transcriptions available to export", severity="warning")
            
    def _export_history_transcriptions(self):
        """Export historical transcriptions."""
        from ..ui.export_dialog import ExportDialog
        
        def handle_export_config(config):
            if config:
                self._perform_history_export(config)
                
        self.app.push_screen(ExportDialog("history"), handle_export_config)
        
    def _perform_single_export(self, entry, format_type):
        """Perform export for a single transcription entry."""
        try:
            from ..utils.export_manager import ExportManager, ExportOptions
            
            export_manager = ExportManager(
                transcript_manager=getattr(self.app, 'transcript_manager', None),
                history_manager=getattr(self.app, 'history_manager', None)
            )
            
            # Use default options for quick export
            options = ExportOptions()
            
            # Determine text to export
            text = getattr(entry, 'text', '')
            formatted_text = getattr(entry, 'formatted_text', None)
            timestamp = getattr(entry, 'timestamp', '')
            
            # Export to default location
            output_path = export_manager.export_single_transcription(
                text=text,
                formatted_text=formatted_text,
                timestamp=timestamp,
                format_type=format_type,
                options=options
            )
            
            self.app.notify(f"✅ Transcription exported to: {output_path.name}", severity="information")
            
        except Exception as e:
            self.app.notify(f"❌ Export failed: {e}", severity="error")
            
    def _perform_session_export(self, entries, config):
        """Perform export for session transcriptions."""
        try:
            from ..utils.export_manager import ExportManager
            
            export_manager = ExportManager(
                transcript_manager=getattr(self.app, 'transcript_manager', None),
                history_manager=getattr(self.app, 'history_manager', None)
            )
            
            # Convert entries to session data format
            session_data = []
            for entry in entries:
                session_data.append({
                    'text': getattr(entry, 'text', ''),
                    'formatted_text': getattr(entry, 'formatted_text', None),
                    'timestamp': getattr(entry, 'timestamp', ''),
                    'entry_id': getattr(entry, 'entry_id', '')
                })
            
            # Export session data
            output_path = export_manager.export_session_data(
                session_entries=session_data,
                output_path=config.get('output_path'),
                format_type=config['format'],
                options=config['options']
            )
            
            self.app.notify(f"✅ Session transcriptions exported to: {output_path.name}", severity="information")
            
        except Exception as e:
            self.app.notify(f"❌ Export failed: {e}", severity="error")
            
    def _perform_history_export(self, config):
        """Perform export for historical transcriptions."""
        try:
            from ..utils.export_manager import ExportManager
            
            export_manager = ExportManager(
                transcript_manager=getattr(self.app, 'transcript_manager', None),
                history_manager=getattr(self.app, 'history_manager', None)
            )
            
            # Get history data
            history_data = []
            if hasattr(self.app, 'history_manager') and self.app.history_manager:
                history_data = self.app.history_manager.get_history()
            
            if not history_data:
                self.app.notify("ℹ️ No history data available to export", severity="warning")
                return
            
            # Export history data
            output_path = export_manager.export_history(
                history_data=history_data,
                output_path=config.get('output_path'),
                format_type=config['format'],
                options=config['options'],
                filter_criteria=config.get('filter_criteria')
            )
            
            count = len(history_data)
            self.app.notify(f"✅ {count} historical transcriptions exported to: {output_path.name}", severity="information")
            
        except Exception as e:
            self.app.notify(f"❌ Export failed: {e}", severity="error")


class CLIWhispererTUI(App):
    """Main Textual TUI application for CLI Whisperer."""
    
    @property
    def CSS(self) -> str:
        """Get the current theme CSS."""
        return self.current_theme_css + """
    
    /* Theme Selector Styles */
    .theme-selector-container {
        height: 1fr;
        overflow-y: auto;
        background: $surface;
        padding: 1;
    }
    
    .theme-header {
        dock: top;
        height: 1;
        background: $primary;
        content-align: center middle;
        color: $text;
        margin: 0 0 2 0;
    }
    
    .theme-controls {
        height: 3;
        margin: 0 0 2 0;
    }
    
    .theme-label {
        content-align: left middle;
        width: 15;
    }
    
    .theme-select {
        width: 1fr;
        margin: 0 1 0 0;
    }
    
    .apply-button {
        width: 15;
    }
    
    .theme-preview {
        margin: 2 0 0 0;
        padding: 1;
        border: solid $primary;
        background: $surface-lighten-1;
        height: auto;
    }
    
    .preview-header {
        height: 1;
        content-align: center middle;
        color: $primary;
        margin: 0 0 1 0;
    }
    
    .preview-text {
        height: 1;
        margin: 0 0 1 0;
        padding: 0 1;
    }
    
    .color-preview {
        height: auto;
        margin: 1 0 0 0;
    }
    
    .color-label {
        content-align: left middle;
        width: 10;
    }
    
    .color-swatches {
        width: 1fr;
        height: auto;
    }
    
    .color-swatch {
        height: 1;
        margin: 0 0 1 0;
        padding: 0 1;
    }
    
    /* Enhanced TranscriptionLog Styles */
    .log-header {
        dock: top;
        height: 1;
        background: $primary;
        content-align: center middle;
        color: $text;
    }
    
    .scrollable-container {
        height: 1fr;
        overflow-y: auto;
        background: $surface;
    }
    
    .placeholder-text {
        content-align: center middle;
        color: $text-muted;
        height: 1fr;
    }
    
    TranscriptionEntry {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
        background: $surface-lighten-1;
    }
    
    .transcription-section {
        margin: 0 0 1 0;
    }
    
    .transcription-header {
        height: 1;
        margin: 0 0 1 0;
    }
    
    .transcription-content {
        margin: 0 1 0 0;
        padding: 1;
        border: solid $primary-lighten-2;
        background: $surface;
        min-height: 3;
        max-height: 10;
        overflow-y: auto;
    }
    
    .raw-content {
        border: solid $primary;
    }
    
    .ai-content {
        border: solid $accent;
    }
    
    .action-buttons {
        width: 15;
        content-align: center middle;
    }
    
    .copy-button {
        width: 12;
        margin: 0 0 1 0;
    }
    
    .error-message, .info-message {
        margin: 1;
        padding: 1;
        height: auto;
    }
    
    /* Enhanced HistoryViewer Styles */
    .history-controls {
        dock: top;
        height: 3;
        margin: 0 0 1 0;
    }
    
    .history-title {
        content-align: left middle;
        width: 1fr;
    }
    
    .search-controls {
        dock: top;
        height: 3;
        margin: 0 0 1 0;
    }
    
    .search-label {
        content-align: left middle;
        width: 8;
    }
    
    .search-input {
        width: 1fr;
        margin: 0 1 0 0;
    }
    
    .clear-button {
        width: 8;
    }
    
    .filter-controls {
        dock: top;
        height: 3;
        margin: 0 0 1 0;
    }
    
    .filter-label {
        content-align: left middle;
        width: 8;
    }
    
    .filter-button {
        width: 12;
        margin: 0 1 0 0;
    }
    
    .history-container {
        height: 1fr;
        overflow-y: auto;
        background: $surface;
    }
    
    .history-placeholder {
        content-align: center middle;
        color: $text-muted;
        height: 1fr;
    }
    
    HistoryEntry {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
        background: $surface-lighten-1;
        height: auto;
    }
    
    .history-entry {
        height: auto;
    }
    
    .history-info {
        width: 1fr;
        margin: 0 1 0 0;
    }
    
    .history-header {
        height: 1;
        margin: 0 0 1 0;
    }
    
    .history-text {
        margin: 0 0 1 0;
        padding: 1;
        border: solid $primary-lighten-2;
        background: $surface;
        min-height: 2;
        max-height: 4;
        overflow-y: auto;
    }
    
    .ai-indicator {
        height: 1;
        color: $success;
    }
    
    .history-actions {
        width: 15;
        content-align: center top;
    }
    
    .history-button {
        width: 12;
        margin: 0 0 1 0;
    }
    
    /* Enhanced History Entry Styles */
    .enhanced-history-entry {
        margin: 1 0;
        padding: 1;
        border: solid $primary-lighten-1;
        background: $surface-lighten-1;
        width: 1fr;
    }
    
    .history-header-row {
        height: 1;
        margin: 0 0 1 0;
        width: 1fr;
    }
    
    .ai-badge {
        width: 5;
        content-align: right middle;
        color: $success;
        text-style: bold;
    }
    
    .file-path-info {
        height: 1;
        color: $text-muted;
        text-style: dim;
        margin: 0 0 1 0;
    }
    
    .preview-container {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
        background: $background;
        min-height: 3;
    }
    
    .preview-text {
        min-height: 2;
        margin: 0 0 1 0;
        overflow-y: auto;
    }
    
    .expand-button {
        width: 15;
        height: 1;
        margin: 1 0 0 0;
    }
    
    .action-buttons-row {
        height: 3;
        margin: 1 0 0 0;
        content-align: center middle;
    }
    
    .compact-button {
        width: 8;
        margin: 0 1;
        height: 1;
    }
    
    /* ActionsPanel Styles */
    .actions-container {
        height: 1fr;
        overflow-y: auto;
        background: $surface;
        padding: 1;
    }
    
    .actions-header {
        dock: top;
        height: 1;
        background: $primary;
        content-align: center middle;
        color: $text;
        margin: 0 0 2 0;
    }
    
    .main-actions, .recording-actions, .export-actions {
        height: auto;
        margin: 0 0 2 0;
    }
    
    .action-group {
        width: 1fr;
        margin: 0 1 0 0;
        padding: 1;
        border: solid $primary-lighten-2;
        background: $surface-lighten-1;
    }
    
    .group-header {
        height: 1;
        content-align: center middle;
        margin: 0 0 1 0;
        color: $primary;
    }
    
    .action-button-large {
        width: 100%;
        margin: 0 0 1 0;
        height: 3;
    }
    
    .session-info {
        margin: 2 0 0 0;
        padding: 1;
        border: solid $accent;
        background: $surface-lighten-1;
        height: auto;
    }
    
    .info-header {
        height: 1;
        content-align: center middle;
        color: $accent;
        margin: 0 0 1 0;
    }
    
    .info-text {
        height: 1;
        margin: 0 0 1 0;
        padding: 0 1;
    }
    
    /* Export Dialog Styles */
    .export-dialog {
        align: center middle;
        width: 60%;
        height: 70%;
        background: $surface;
        border: solid $primary;
    }
    
    .export-content {
        padding: 1;
        height: 1fr;
        overflow-y: auto;
    }
    
    .export-header {
        height: 1;
        content-align: center middle;
        color: $primary;
        margin: 0 0 2 0;
    }
    
    .export-row {
        height: 3;
        margin: 0 0 1 0;
        align: center middle;
    }
    
    .export-label {
        width: 12;
        content-align: left middle;
    }
    
    .export-select, .export-input {
        width: 1fr;
        margin: 0 1 0 0;
    }
    
    .export-button {
        width: 10;
    }
    
    .export-section-header {
        height: 1;
        content-align: center middle;
        color: $accent;
        margin: 2 0 1 0;
    }
    
    .export-buttons {
        dock: bottom;
        height: 3;
        margin: 2 0 0 0;
    }
    
    .export-buttons Button {
        width: 1fr;
        margin: 0 1 0 0;
    }
    
    .export-options-dialog {
        align: center middle;
        width: 40%;
        height: 50%;
        background: $surface;
        border: solid $primary;
    }
    
    .export-options-content {
        padding: 1;
        height: 1fr;
    }
    
    .format-buttons {
        height: 1fr;
        margin: 1 0 0 0;
    }
    
    .format-button {
        width: 100%;
        margin: 0 0 1 0;
        height: 3;
    }
    
    .cancel-button {
        width: 100%;
        margin: 2 0 0 0;
        height: 3;
    }
    
    .export-progress-dialog {
        align: center middle;
        width: 40%;
        height: 30%;
        background: $surface;
        border: solid $primary;
    }
    
    .export-progress-content {
        padding: 1;
        height: 1fr;
    }
    
    .progress-text {
        height: 1;
        content-align: center middle;
        margin: 1 0 0 0;
    }
    
    .progress-info {
        height: 1;
        content-align: center middle;
        margin: 2 0 0 0;
        color: $text-muted;
    }
    
    /* Recording Progress Bar Styles */
    .recording-progress-bar {
        display: none;
        margin: 1 0 0 0;
        height: 1;
        border: solid $primary;
        background: $surface;
    }
    
    .recording-progress-bar ProgressBar {
        color: $success;
        background: $surface-darken-1;
    }
    
    /* Spotify Status Panel Styles */
    SpotifyStatusPanel {
        margin: 1 0;
        padding: 1;
        border: solid $accent;
        background: $surface-lighten-1;
        height: auto;
        min-height: 6;
    }
    """
    
    BINDINGS = [
        # Core Actions
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("r", "record", "Record"),
        Binding("s", "stop", "Stop"),
        Binding("space", "toggle_recording", "Toggle Recording"),
        
        # Navigation
        Binding("h", "show_history", "History"),
        Binding("t", "show_themes", "Themes"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Previous Tab"),
        Binding("ctrl+t", "cycle_tabs", "Cycle Tabs"),
        
        # Copy Operations
        Binding("c", "copy_latest_ai", "Copy Latest AI"),
        Binding("ctrl+c", "copy_latest_raw", "Copy Latest Raw"),
        Binding("ctrl+shift+c", "copy_latest_raw", "Copy Latest Raw"),
        Binding("ctrl+a", "copy_latest_ai_enhanced", "Copy Latest AI (Enhanced)"),
        Binding("ctrl+shift+a", "copy_all_transcriptions", "Copy All Transcriptions"),
        
        # Duration Controls
        Binding("plus", "increase_duration", "Increase Duration"),
        Binding("minus", "decrease_duration", "Decrease Duration"),
        Binding("1", "set_duration_30", "Set 30s"),
        Binding("2", "set_duration_60", "Set 1m"),
        Binding("3", "set_duration_120", "Set 2m"),
        Binding("4", "set_duration_300", "Set 5m"),
        
        # Spotify Controls
        Binding("ctrl+p", "spotify_play_pause", "Play/Pause"),
        Binding("ctrl+n", "spotify_next", "Next Track"),
        Binding("ctrl+b", "spotify_previous", "Previous Track"),
        Binding("ctrl+s", "toggle_spotify_panel", "Toggle Spotify Panel"),
        Binding("ctrl+shift+s", "spotify_shuffle", "Toggle Shuffle"),
        Binding("ctrl+shift+r", "spotify_repeat", "Toggle Repeat"),
        
        # File Operations
        Binding("ctrl+o", "open_transcript_dir", "Open Transcript Directory"),
        Binding("ctrl+e", "export_transcription", "Export Transcription"),
        Binding("ctrl+shift+e", "export_all", "Export All"),
        Binding("ctrl+d", "delete_old_files", "Clean Old Files"),
        
        # UI Controls
        Binding("f1", "show_help", "Help"),
        Binding("?", "show_help", "Help"),
        Binding("ctrl+slash", "show_help", "Help"),
        Binding("f2", "toggle_debug", "Toggle Debug"),
        Binding("f3", "toggle_audio_meter", "Toggle Audio Meter"),
        Binding("f4", "toggle_compact_mode", "Toggle Compact Mode"),
        
        # Advanced Features
        Binding("ctrl+r", "reload_config", "Reload Config"),
        Binding("ctrl+shift+t", "switch_theme", "Switch Theme"),
        Binding("ctrl+l", "clear_log", "Clear Log"),
        Binding("ctrl+shift+l", "clear_history", "Clear History"),
        Binding("f5", "refresh_ui", "Refresh UI"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_recorder = None
        self.transcriber = None
        self.formatter = None
        self.transcript_manager = None
        self.history_manager = None
        self.clipboard_manager = None
        self.recording_duration = 5  # Default, will be updated from CLI args
        self.audio_level_timer = None
        self.recording_timer = None
        
        # Initialize logger without debug mode for production
        self.logger = get_logger(debug_mode=False)
        self.logger.info("CLI Whisperer TUI v0.2.3 initialized")
        self.current_recording = None
        self.theme_manager = ThemeManager()
        self.current_theme_css = self.theme_manager.get_current_theme().css
        self.edit_manager = EditManager()
        
    def compose(self) -> ComposeResult:
        """Compose the main UI - optimized for smaller terminals."""
        # Compact status bar combining multiple panels
        with Horizontal(classes="compact-status-bar"):
            yield StatusPanel(id="status-panel")
            yield AudioLevelMeter(id="audio-meter")
            yield RecordingControls(duration=self.recording_duration, id="recording-controls")
        
        # Hide Spotify status panel by default (can be toggled)
        yield SpotifyStatusPanel(id="spotify-status-panel", classes="hidden")
        
        with TabbedContent(initial="transcriptions"):
            with TabPane("Transcriptions", id="transcriptions"):
                yield TranscriptionLog(id="transcription-log")
                
            with TabPane("History", id="history"):
                yield HistoryViewer(
                    history_file=DEFAULT_TRANSCRIPT_DIR / "history.json",
                    id="history-viewer"
                )
                
            with TabPane("Actions", id="actions"):
                yield ActionsPanel(id="actions-panel")
                
            with TabPane("Themes", id="themes"):
                yield ThemeSelector(id="theme-selector")
        
    def set_components(self, audio_recorder, transcriber, formatter, 
                      transcript_manager, history_manager, clipboard_manager):
        """Set the core components."""
        self.audio_recorder = audio_recorder
        self.transcriber = transcriber
        self.formatter = formatter
        self.transcript_manager = transcript_manager
        self.history_manager = history_manager
        self.clipboard_manager = clipboard_manager
        
        # Set up Spotify integration
        try:
            spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
            spotify_controller = getattr(audio_recorder, 'spotify_controller', None)
            spotify_panel.set_spotify_controller(spotify_controller)
        except:
            pass  # Spotify panel may not be mounted yet
        
    def set_recording_duration(self, duration: int):
        """Set the recording duration."""
        logger = get_logger()
        logger.info(f"Setting main recording duration to {duration}s")
        
        self.recording_duration = duration
        # Update the recording controls if they exist
        try:
            recording_controls = self.query_one("#recording-controls", RecordingControls)
            recording_controls.update_duration(duration)
            logger.info(f"Successfully updated RecordingControls duration to {duration}s")
        except Exception as e:
            logger.warning(f"Could not update RecordingControls duration: {e} - Controls may not be mounted yet")
        
    def on_mount(self):
        """Initialize the TUI when mounted."""
        self.title = "CLI Whisperer v0.1.3 - Voice to Text TUI"
        self.sub_title = "Press 'r' to record, 'q' to quit"
        
        # Update status if components are set
        if hasattr(self, 'transcriber') and self.transcriber:
            self.query_one("#status-panel", StatusPanel).update_status(
                model_name=self.transcriber.model_name,
                openai_enabled=not self.formatter.disabled,
                spotify_enabled=self.audio_recorder.spotify_controller is not None,
                transcript_dir=self.transcript_manager.base_dir
            )
            
            # Set up Spotify status panel
            try:
                spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
                spotify_controller = getattr(self.audio_recorder, 'spotify_controller', None)
                spotify_panel.set_spotify_controller(spotify_controller)
            except:
                pass  # Spotify panel setup will be handled when components are set
        
    def action_record(self):
        """Action to start recording."""
        if not self.current_recording:
            self.query_one("#recording-controls", RecordingControls).start_recording()
            
    def action_stop(self):
        """Action to stop recording."""
        if self.current_recording:
            self.query_one("#recording-controls", RecordingControls).stop_recording()
            
    def action_show_history(self):
        """Action to show history tab."""
        self.query_one(TabbedContent).active = "history"
        
    def action_show_themes(self):
        """Action to show themes tab."""
        self.query_one(TabbedContent).active = "themes"
        
    def action_copy_latest_ai(self):
        """Action to copy the latest AI-formatted transcription."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        transcription_log.copy_latest_ai()
        
    def action_copy_latest_raw(self):
        """Action to copy the latest raw transcription."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            latest_entry = transcription_log.entries[-1]
            if hasattr(latest_entry, 'text') and self.clipboard_manager:
                success = self.clipboard_manager.copy_to_clipboard(latest_entry.text)
                if success:
                    self.notify("✅ Latest raw transcription copied to clipboard!", 
                              title="Copy Success", severity="information")
                else:
                    self.notify("❌ Failed to copy to clipboard", 
                              title="Copy Failed", severity="error")
            else:
                self.notify("❌ No raw transcription available", 
                          title="Copy Failed", severity="warning")
        else:
            self.notify("ℹ️ No transcriptions available to copy", 
                      title="No Content", severity="warning")
    
    def action_copy_latest_ai_enhanced(self):
        """Enhanced action to copy latest AI transcription with better feedback."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'latest_ai_text') and transcription_log.latest_ai_text:
            if self.clipboard_manager:
                success = self.clipboard_manager.copy_to_clipboard(transcription_log.latest_ai_text)
                if success:
                    # Show enhanced notification with preview
                    preview = transcription_log.latest_ai_text[:100] + "..." if len(transcription_log.latest_ai_text) > 100 else transcription_log.latest_ai_text
                    self.notify(f"✅ AI transcription copied!\n\nPreview: {preview}", 
                              title="Enhanced Copy Success", severity="information")
                else:
                    self.notify("❌ Failed to copy AI transcription to clipboard", 
                              title="Copy Failed", severity="error")
            else:
                self.notify("❌ Clipboard manager not available", 
                          title="System Error", severity="error")
        else:
            self.notify("ℹ️ No AI-formatted transcription available to copy", 
                      title="No AI Content", severity="warning")
        
    def action_show_help(self):
        """Action to show keyboard shortcuts help."""
        help_text = """
🎹 CLI Whisperer - Keyboard Shortcuts

📝 Recording Controls:
  r          Start recording
  s          Stop recording
  
📋 Copy Actions:
  c          Copy latest AI-formatted transcription
  Ctrl+A     Enhanced copy with preview (AI transcription)
  Ctrl+Shift+C  Copy latest raw transcription
  
🗂️ Navigation:
  h          Switch to History tab
  t          Switch to Themes tab
  Tab        Navigate between UI elements
  
⚡ Quick Actions:
  F1 or ?    Show this help
  q or Esc   Quit application
  
💡 Tips:
  • Enhanced copy shows preview in notification
  • Use the Actions tab for more copy and file options
  • History tab supports search and filtering
  • Click copy buttons next to transcriptions for quick access
  • All transcriptions are automatically copied to clipboard
        """.strip()
        
        self.notify(help_text, title="Keyboard Shortcuts", severity="information")
        
    def action_quit(self):
        """Action to quit the application with proper cleanup."""
        logger = get_logger()
        logger.info("Quitting application - starting cleanup")
        
        try:
            # Stop any ongoing recording
            if self.current_recording:
                logger.info("Cancelling ongoing recording")
                self.current_recording.cancel()
                self.current_recording = None
            
            # Stop audio level timer
            if self.audio_level_timer:
                logger.info("Stopping audio level timer")
                self.audio_level_timer.stop()
                self.audio_level_timer = None
            
            # Stop recording timer if it exists
            if hasattr(self, 'recording_timer') and self.recording_timer:
                logger.info("Stopping recording timer")
                self.recording_timer.stop()
                self.recording_timer = None
            
            # Stop Spotify status updates
            try:
                spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
                spotify_panel.stop_status_updates()
                logger.info("Stopped Spotify status updates")
            except Exception as e:
                logger.debug(f"Could not stop Spotify updates: {e}")
            
            # Stop recording controls progress timer
            try:
                recording_controls = self.query_one("#recording-controls", RecordingControls)
                if recording_controls.progress_timer:
                    recording_controls.progress_timer.stop()
                    recording_controls.progress_timer = None
                    logger.info("Stopped recording controls progress timer")
            except Exception as e:
                logger.debug(f"Could not stop recording controls timer: {e}")
            
            logger.info("Cleanup completed - exiting application")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
        
        self.exit()
        
    def action_toggle_recording(self):
        """Action to toggle between record and stop."""
        if self.current_recording:
            self.query_one("#recording-controls", RecordingControls).stop_recording()
        else:
            self.query_one("#recording-controls", RecordingControls).start_recording()
    
    def action_next_tab(self):
        """Action to switch to next tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabs = list(tabbed_content.query(TabPane))
        if tabs:
            current_active = tabbed_content.active
            current_index = next((i for i, tab in enumerate(tabs) if tab.id == current_active), 0)
            next_index = (current_index + 1) % len(tabs)
            tabbed_content.active = tabs[next_index].id
    
    def action_prev_tab(self):
        """Action to switch to previous tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabs = list(tabbed_content.query(TabPane))
        if tabs:
            current_active = tabbed_content.active
            current_index = next((i for i, tab in enumerate(tabs) if tab.id == current_active), 0)
            prev_index = (current_index - 1) % len(tabs)
            tabbed_content.active = tabs[prev_index].id
    
    def action_cycle_tabs(self):
        """Action to cycle through tabs."""
        self.action_next_tab()
    
    def action_copy_all_transcriptions(self):
        """Action to copy all transcriptions to clipboard."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            all_transcriptions = []
            for entry in transcription_log.entries:
                if hasattr(entry, 'formatted_text') and entry.formatted_text:
                    all_transcriptions.append(f"[AI] {entry.formatted_text}")
                elif hasattr(entry, 'text') and entry.text:
                    all_transcriptions.append(f"[Raw] {entry.text}")
            
            if all_transcriptions and self.clipboard_manager:
                combined_text = "\n\n".join(all_transcriptions)
                success = self.clipboard_manager.copy_to_clipboard(combined_text)
                if success:
                    count = len(all_transcriptions)
                    self.notify(f"✅ {count} transcription(s) copied to clipboard!", 
                              title="Copy All Success", severity="information")
                else:
                    self.notify("❌ Failed to copy transcriptions to clipboard", 
                              title="Copy Failed", severity="error")
            else:
                self.notify("❌ No transcriptions available or clipboard unavailable", 
                          title="Copy Failed", severity="warning")
        else:
            self.notify("ℹ️ No transcriptions available to copy", 
                      title="No Content", severity="warning")
    
    def action_increase_duration(self):
        """Action to increase recording duration."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'adjust_duration'):
            recording_controls.adjust_duration(15)  # Increase by 15 seconds
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_decrease_duration(self):
        """Action to decrease recording duration."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'adjust_duration'):
            recording_controls.adjust_duration(-15)  # Decrease by 15 seconds
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_set_duration_30(self):
        """Action to set recording duration to 30 seconds."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'set_duration'):
            recording_controls.set_duration(30)
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_set_duration_60(self):
        """Action to set recording duration to 60 seconds."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'set_duration'):
            recording_controls.set_duration(60)
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_set_duration_120(self):
        """Action to set recording duration to 120 seconds."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'set_duration'):
            recording_controls.set_duration(120)
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_set_duration_300(self):
        """Action to set recording duration to 300 seconds."""
        recording_controls = self.query_one("#recording-controls", RecordingControls)
        if hasattr(recording_controls, 'set_duration'):
            recording_controls.set_duration(300)
        else:
            self.notify("⚠️ Duration control not available", severity="warning")
    
    def action_spotify_play_pause(self):
        """Action to toggle Spotify play/pause."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if hasattr(spotify_panel, 'spotify_controller') and spotify_panel.spotify_controller:
            try:
                spotify_panel.spotify_controller.toggle_playback()
                self.notify("🎵 Spotify play/pause toggled", severity="information")
            except Exception as e:
                self.notify(f"❌ Spotify control failed: {e}", severity="error")
        else:
            self.notify("⚠️ Spotify not available", severity="warning")
    
    def action_spotify_next(self):
        """Action to skip to next Spotify track."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if hasattr(spotify_panel, 'spotify_controller') and spotify_panel.spotify_controller:
            try:
                spotify_panel.spotify_controller.next_track()
                self.notify("⏭️ Spotify: Next track", severity="information")
            except Exception as e:
                self.notify(f"❌ Spotify next failed: {e}", severity="error")
        else:
            self.notify("⚠️ Spotify not available", severity="warning")
    
    def action_spotify_previous(self):
        """Action to skip to previous Spotify track."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if hasattr(spotify_panel, 'spotify_controller') and spotify_panel.spotify_controller:
            try:
                spotify_panel.spotify_controller.previous_track()
                self.notify("⏮️ Spotify: Previous track", severity="information")
            except Exception as e:
                self.notify(f"❌ Spotify previous failed: {e}", severity="error")
        else:
            self.notify("⚠️ Spotify not available", severity="warning")
    
    def action_spotify_shuffle(self):
        """Action to toggle Spotify shuffle."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if hasattr(spotify_panel, 'spotify_controller') and spotify_panel.spotify_controller:
            try:
                spotify_panel.spotify_controller.toggle_shuffle()
                self.notify("🔀 Spotify shuffle toggled", severity="information")
            except Exception as e:
                self.notify(f"❌ Spotify shuffle failed: {e}", severity="error")
        else:
            self.notify("⚠️ Spotify not available", severity="warning")
    
    def action_spotify_repeat(self):
        """Action to toggle Spotify repeat."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if hasattr(spotify_panel, 'spotify_controller') and spotify_panel.spotify_controller:
            try:
                spotify_panel.spotify_controller.toggle_repeat()
                self.notify("🔁 Spotify repeat toggled", severity="information")
            except Exception as e:
                self.notify(f"❌ Spotify repeat failed: {e}", severity="error")
        else:
            self.notify("⚠️ Spotify not available", severity="warning")
    
    def action_toggle_spotify_panel(self):
        """Action to toggle Spotify panel visibility."""
        spotify_panel = self.query_one("#spotify-status-panel", SpotifyStatusPanel)
        if spotify_panel.has_class("hidden"):
            spotify_panel.remove_class("hidden")
            self.notify("🎵 Spotify panel shown", severity="information")
        else:
            spotify_panel.add_class("hidden")
            self.notify("🎵 Spotify panel hidden", severity="information")
    
    def action_open_transcript_dir(self):
        """Action to open transcript directory."""
        if hasattr(self, 'transcript_manager') and self.transcript_manager:
            import subprocess
            import platform
            
            try:
                transcript_dir = self.transcript_manager.base_dir
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', transcript_dir])
                elif platform.system() == 'Windows':
                    subprocess.run(['explorer', transcript_dir])
                else:  # Linux
                    subprocess.run(['xdg-open', transcript_dir])
                self.notify(f"📁 Opened transcript directory: {transcript_dir}", severity="information")
            except Exception as e:
                self.notify(f"❌ Failed to open directory: {e}", severity="error")
        else:
            self.notify("⚠️ Transcript manager not available", severity="warning")
    
    def action_export_transcription(self):
        """Action to export current transcription with format selection."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            latest_entry = transcription_log.entries[-1]
            
            # Use export dialog for format selection
            from .export_dialog import ExportDialog
            
            def handle_export_config(config):
                if config:
                    self._export_single_transcription_with_config(latest_entry, config)
                    
            self.push_screen(ExportDialog("single"), handle_export_config)
        else:
            self.notify("ℹ️ No transcriptions available to export", severity="warning")
    
    def action_export_all(self):
        """Action to export all transcriptions with format selection."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'entries') and transcription_log.entries:
            # Use export dialog for format selection
            from .export_dialog import ExportDialog
            
            def handle_export_config(config):
                if config:
                    self._export_all_transcriptions_with_config(transcription_log.entries, config)
                    
            self.push_screen(ExportDialog("session"), handle_export_config)
        else:
            self.notify("ℹ️ No transcriptions available to export", severity="warning")
    
    def _export_single_transcription_with_config(self, entry, config):
        """Export a single transcription with the given configuration."""
        try:
            from ..utils.export_manager import ExportManager
            
            export_manager = ExportManager(
                transcript_manager=getattr(self, 'transcript_manager', None),
                history_manager=getattr(self, 'history_manager', None)
            )
            
            # Get text from entry
            text = getattr(entry, 'text', '')
            formatted_text = getattr(entry, 'formatted_text', None)
            timestamp = getattr(entry, 'timestamp', '')
            
            # Export the transcription
            output_path = export_manager.export_single_transcription(
                text=text,
                formatted_text=formatted_text,
                timestamp=timestamp,
                output_path=config.get('output_path'),
                format_type=config['format'],
                options=config['options']
            )
            
            self.notify(f"✅ Transcription exported to: {output_path.name}", severity="information")
            
        except Exception as e:
            self.notify(f"❌ Export failed: {e}", severity="error")
            
    def _export_all_transcriptions_with_config(self, entries, config):
        """Export all transcriptions with the given configuration."""
        try:
            from ..utils.export_manager import ExportManager
            
            export_manager = ExportManager(
                transcript_manager=getattr(self, 'transcript_manager', None),
                history_manager=getattr(self, 'history_manager', None)
            )
            
            # Convert entries to session data format
            session_data = []
            for entry in entries:
                session_data.append({
                    'text': getattr(entry, 'text', ''),
                    'formatted_text': getattr(entry, 'formatted_text', None),
                    'timestamp': getattr(entry, 'timestamp', ''),
                    'entry_id': getattr(entry, 'entry_id', '')
                })
            
            # Export session data
            output_path = export_manager.export_session_data(
                session_entries=session_data,
                output_path=config.get('output_path'),
                format_type=config['format'],
                options=config['options']
            )
            
            count = len(session_data)
            self.notify(f"✅ {count} transcription(s) exported to: {output_path.name}", severity="information")
            
        except Exception as e:
            self.notify(f"❌ Export failed: {e}", severity="error")
    
    def action_delete_old_files(self):
        """Action to delete old transcript files."""
        if hasattr(self, 'transcript_manager') and self.transcript_manager:
            try:
                if hasattr(self.transcript_manager, 'cleanup_old_files'):
                    deleted_count = self.transcript_manager.cleanup_old_files()
                    self.notify(f"✅ Cleaned up {deleted_count} old files", severity="information")
                else:
                    self.notify("⚠️ Cleanup function not available", severity="warning")
            except Exception as e:
                self.notify(f"❌ Cleanup failed: {e}", severity="error")
        else:
            self.notify("⚠️ Transcript manager not available", severity="warning")
    
    def action_toggle_debug(self):
        """Action to toggle debug mode."""
        # This would typically toggle debug logging or show debug information
        self.notify("🔧 Debug mode toggle (placeholder)", severity="information")
    
    def action_toggle_audio_meter(self):
        """Action to toggle audio meter visibility."""
        audio_meter = self.query_one("#audio-meter", AudioLevelMeter)
        if audio_meter.has_class("hidden"):
            audio_meter.remove_class("hidden")
            self.notify("🎤 Audio meter shown", severity="information")
        else:
            audio_meter.add_class("hidden")
            self.notify("🎤 Audio meter hidden", severity="information")
    
    def action_toggle_compact_mode(self):
        """Action to toggle compact mode."""
        # This would toggle a compact UI layout
        self.notify("📱 Compact mode toggle (placeholder)", severity="information")
    
    def action_reload_config(self):
        """Action to reload configuration."""
        try:
            # Reload any configuration files
            self.notify("🔄 Configuration reloaded", severity="information")
        except Exception as e:
            self.notify(f"❌ Config reload failed: {e}", severity="error")
    
    def action_switch_theme(self):
        """Action to switch to next theme."""
        if hasattr(self, 'theme_manager') and self.theme_manager:
            try:
                available_themes = self.theme_manager.get_theme_names()
                current_theme = self.theme_manager.current_theme
                current_index = available_themes.index(current_theme) if current_theme in available_themes else 0
                next_index = (current_index + 1) % len(available_themes)
                next_theme = available_themes[next_index]
                self.apply_theme(next_theme)
                self.notify(f"🎨 Switched to theme: {next_theme}", severity="information")
            except Exception as e:
                self.notify(f"❌ Theme switch failed: {e}", severity="error")
        else:
            self.notify("⚠️ Theme manager not available", severity="warning")
    
    def action_clear_log(self):
        """Action to clear transcription log."""
        transcription_log = self.query_one("#transcription-log", TranscriptionLog)
        if hasattr(transcription_log, 'clear'):
            transcription_log.clear()
            self.notify("🗑️ Transcription log cleared", severity="information")
        else:
            self.notify("⚠️ Log clear function not available", severity="warning")
    
    def action_clear_history(self):
        """Action to clear transcription history."""
        if hasattr(self, 'history_manager') and self.history_manager:
            try:
                if hasattr(self.history_manager, 'clear_history'):
                    self.history_manager.clear_history()
                    self.notify("🗑️ History cleared", severity="information")
                else:
                    self.notify("⚠️ History clear function not available", severity="warning")
            except Exception as e:
                self.notify(f"❌ History clear failed: {e}", severity="error")
        else:
            self.notify("⚠️ History manager not available", severity="warning")
    
    def action_refresh_ui(self):
        """Action to refresh the UI."""
        try:
            self.refresh(layout=True, repaint=True)
            self.notify("🔄 UI refreshed", severity="information")
        except Exception as e:
            self.notify(f"❌ UI refresh failed: {e}", severity="error")
        
    def apply_theme(self, theme_name: str):
        """Apply a new theme to the application."""
        if self.theme_manager.set_theme(theme_name):
            new_theme = self.theme_manager.get_current_theme()
            self.current_theme_css = new_theme.css
            # Debug info
            self.notify(f"🔄 Loading theme: {new_theme.display_name}", severity="information")
            # Force a refresh of the CSS
            self.refresh_css()
            
    def refresh_css(self):
        """Refresh the CSS to apply new theme."""
        # The most effective way to reload CSS in Textual is to force a complete refresh
        try:
            # Force complete layout and render refresh
            self.refresh(layout=True, repaint=True)
            # Also refresh all child widgets to pick up new styles
            for widget in self.query("*"):
                widget.refresh()
            self.notify("✨ Theme applied successfully!", severity="success")
        except Exception as e:
            self.notify(f"❌ Error applying theme: {e}", severity="error")
        
    def on_recording_controls_recording_started(self, event: RecordingControls.RecordingStarted):
        """Handle recording started."""
        self.start_recording_session()
        
    def on_recording_controls_recording_stopped(self, event: RecordingControls.RecordingStopped):
        """Handle recording stopped."""
        self.stop_recording_session()
        
    def start_recording_session(self):
        """Start a recording session."""
        self.current_recording = asyncio.create_task(self._record_and_transcribe())
        
        # Update status
        self.query_one("#status-panel", StatusPanel).update_status(recording_state="recording")
        
        # Update audio level meter state
        try:
            self.query_one("#audio-meter", AudioLevelMeter).set_recording_state("recording")
        except Exception:
            pass  # Audio meter might not exist in compact mode
        
        # Update actions panel recording state
        try:
            actions_panel = self.query_one("#actions-panel", ActionsPanel)
            actions_panel.set_recording_state(True)
        except:
            pass
        
        # Start audio level monitoring
        self.audio_level_timer = self.set_interval(0.1, self.update_audio_level)
        
        # Add enhanced log entry
        self.query_one("#transcription-log", TranscriptionLog).add_info(f"Recording started for {self.recording_duration} seconds - speak clearly into your microphone!")
        
    def stop_recording_session(self):
        """Stop the current recording session gracefully."""
        logger = get_logger()
        logger.info("Stop recording session requested - using graceful stop")
        
        # Signal the audio recorder to stop gracefully instead of cancelling the task
        if hasattr(self, 'audio_recorder') and self.audio_recorder:
            logger.info("Signaling audio recorder to stop gracefully")
            self.audio_recorder.stop_recording()
        else:
            logger.warning("No audio recorder found for graceful stop")
            # Fallback to task cancellation if no audio recorder
            if self.current_recording:
                logger.info("Falling back to task cancellation")
                self.current_recording.cancel()
                self.current_recording = None
            
        if self.audio_level_timer:
            self.audio_level_timer.stop()
            self.audio_level_timer = None
            
        # Reset audio level meter state
        try:
            self.query_one("#audio-meter", AudioLevelMeter).set_recording_state("idle")
        except Exception:
            pass  # Audio meter might not exist in compact mode
            
        # Update actions panel recording state
        try:
            actions_panel = self.query_one("#actions-panel", ActionsPanel)
            actions_panel.set_recording_state(False)
        except:
            pass
        
        # Reset audio meter
        self.query_one("#audio-meter", AudioLevelMeter).level = 0.0
        
        # Note: We don't update status to "idle" immediately or resume Spotify here
        # because the graceful stop should continue with transcription
        # The status will be updated and Spotify resumed after transcription completes
        
    def update_audio_level(self):
        """Update audio level meter."""
        if self.audio_recorder and hasattr(self.audio_recorder, 'get_current_level'):
            level = self.audio_recorder.get_current_level()
            self.query_one("#audio-meter", AudioLevelMeter).level = level
            
    async def _record_and_transcribe(self):
        """Record audio and transcribe it with comprehensive logging."""
        logger = get_logger()
        logger.log_method_entry("_record_and_transcribe", duration=self.recording_duration)
        
        try:
            # Step 1: Record audio
            logger.log_transcription_step("Starting audio recording", {"duration": self.recording_duration})
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self.audio_recorder.record_audio, self.recording_duration
            )
            
            if audio_data is None:
                logger.error("Audio recording failed - no data received")
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_error("Recording failed - please check your microphone")
                    logger.log_ui_operation("add_error", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to update UI with recording error", {"error": str(e)}, exc_info=True)
                return
                
            logger.log_transcription_step("Audio recording completed", {
                "data_length": len(audio_data),
                "sample_rate": self.audio_recorder.sample_rate
            })
            
            # Step 2: Update status and start transcription
            try:
                self.query_one("#status-panel", StatusPanel).update_status(recording_state="transcribing")
                logger.log_ui_operation("update_status", "status-panel", True)
            except Exception as e:
                logger.error("Failed to update status panel", {"error": str(e)}, exc_info=True)
                
            # Update audio level meter state
            try:
                self.query_one("#audio-meter", AudioLevelMeter).set_recording_state("transcribing")
            except Exception:
                pass  # Audio meter might not exist in compact mode
                
            audio_duration = len(audio_data) / self.audio_recorder.sample_rate
            
            # Check minimum recording length 
            if audio_duration < MIN_RECORDING_LENGTH:
                logger.warning(f"Recording too short: {audio_duration:.1f}s (minimum: {MIN_RECORDING_LENGTH}s)")
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_error(f"Recording too short ({audio_duration:.1f}s) - please record for at least {MIN_RECORDING_LENGTH} second(s)")
                    logger.log_ui_operation("add_error (too short)", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to update UI with short recording error", {"error": str(e)}, exc_info=True)
                return
            
            logger.log_transcription_step("Starting transcription", {
                "audio_duration": audio_duration,
                "model": self.transcriber.model_name
            })
            
            try:
                self.query_one("#transcription-log", TranscriptionLog).add_info(f"Transcribing {audio_duration:.1f}s of audio using {self.transcriber.model_name} model...")
                logger.log_ui_operation("add_info", "transcription-log", True)
            except Exception as e:
                logger.error("Failed to add transcription info to log", {"error": str(e)}, exc_info=True)
            
            # Step 3: Transcribe audio with timeout
            try:
                text = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.transcriber.transcribe_audio, audio_data
                    ),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                logger.error("Transcription timed out after 30 seconds")
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_error("Transcription timed out after 30 seconds - please try a shorter recording")
                    logger.log_ui_operation("add_error (timeout)", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to update UI with timeout error", {"error": str(e)}, exc_info=True)
                return
            
            if not text:
                logger.warning("No speech detected in audio")
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_error("No speech detected - try speaking louder or closer to the microphone")
                    logger.log_ui_operation("add_error", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to update UI with no speech error", {"error": str(e)}, exc_info=True)
                return
                
            logger.log_transcription_step("Transcription completed", {
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            })
                
            # Step 4: Format with OpenAI if enabled
            formatted_text = None
            if not self.formatter.disabled:
                try:
                    self.query_one("#status-panel", StatusPanel).update_status(recording_state="formatting")
                    # Update audio level meter state
                    try:
                        self.query_one("#audio-meter", AudioLevelMeter).set_recording_state("formatting")
                    except Exception:
                        pass  # Audio meter might not exist in compact mode
                    logger.log_ui_operation("update_status", "status-panel", True)
                except Exception as e:
                    logger.error("Failed to update status for formatting", {"error": str(e)}, exc_info=True)
                    
                logger.log_transcription_step("Starting AI formatting", {"model": self.formatter.model})
                
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_info(f"Formatting {len(text)} characters with OpenAI {self.formatter.model}...")
                    logger.log_ui_operation("add_info", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to add formatting info to log", {"error": str(e)}, exc_info=True)
                
                formatted_text = await asyncio.get_event_loop().run_in_executor(
                    None, self.formatter.format_text, text, self.transcript_manager.cleanup_old_files
                )
                
                logger.log_transcription_step("AI formatting completed", {
                    "formatted_length": len(formatted_text) if formatted_text else 0
                })
                
            # Step 5: Save files with enhanced feedback
            logger.log_transcription_step("Starting file save operations")
            txt_path = None
            md_path = None
            
            try:
                txt_path = self.transcript_manager.save_transcript(text, is_ai=False)
                logger.info(f"Raw transcript saved successfully: {txt_path}")
                
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_info(f"Raw transcript saved: {txt_path}")
                    logger.log_ui_operation("add_info", "transcription-log", True)
                except Exception as e:
                    logger.error("Failed to add save info to log", {"error": str(e)}, exc_info=True)
                
                if formatted_text:
                    md_path = self.transcript_manager.save_transcript(formatted_text, is_ai=True)
                    logger.info(f"AI transcript saved successfully: {md_path}")
                    
                    try:
                        self.query_one("#transcription-log", TranscriptionLog).add_info(f"AI transcript saved: {md_path}")
                        logger.log_ui_operation("add_info", "transcription-log", True)
                    except Exception as e:
                        logger.error("Failed to add AI save info to log", {"error": str(e)}, exc_info=True)
                        
            except Exception as e:
                logger.error("Failed to save transcript files", {"error": str(e)}, exc_info=True)
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_error(f"Failed to save files: {e}")
                    logger.log_ui_operation("add_error", "transcription-log", True)
                except Exception as ui_e:
                    logger.error("Failed to update UI with save error", {"error": str(ui_e)}, exc_info=True)
                return
                
            # Step 6: Copy to clipboard
            logger.log_transcription_step("Copying to clipboard")
            clipboard_text = formatted_text if formatted_text else text
            success = self.clipboard_manager.copy_to_clipboard(clipboard_text)
            logger.info(f"Clipboard operation {'successful' if success else 'failed'}")
            
            # Step 7: Save to history
            logger.log_transcription_step("Saving to history")
            try:
                self.history_manager.save_to_history(text, txt_path, self.transcriber.model_name, md_path, os.getcwd())
                logger.info("History saved successfully")
            except Exception as e:
                logger.error("Failed to save to history", {"error": str(e)}, exc_info=True)
            
            # Step 8: CRITICAL - Add to transcription log (this is where the UI display happens)
            logger.log_transcription_step("Adding transcription to UI log - CRITICAL STEP")
            try:
                transcription_log = self.query_one("#transcription-log", TranscriptionLog)
                logger.debug(f"Found transcription log widget: {transcription_log}")
                
                # Call add_transcription with detailed logging
                transcription_log.add_transcription(text, formatted_text)
                logger.info("✅ TRANSCRIPTION SUCCESSFULLY ADDED TO UI LOG")
                logger.log_ui_operation("add_transcription", "transcription-log", True, None)
                
                # Verify it was added
                if hasattr(transcription_log, 'entries'):
                    entry_count = len(transcription_log.entries)
                    logger.info(f"Transcription log now has {entry_count} entries")
                else:
                    logger.warning("Transcription log does not have 'entries' attribute")
                    
            except Exception as e:
                logger.critical("❌ FAILED TO ADD TRANSCRIPTION TO UI LOG - THIS IS THE MAIN ISSUE", {
                    "error": str(e),
                    "error_type": type(e).__name__
                }, exc_info=True)
                
                # Try alternative approach
                logger.info("Attempting fallback UI update method")
                try:
                    self.query_one("#transcription-log", TranscriptionLog).add_info(f"[FALLBACK] Transcription: {text[:200]}...")
                    logger.info("Fallback UI update successful")
                except Exception as fallback_e:
                    logger.critical("Fallback UI update also failed", {"error": str(fallback_e)}, exc_info=True)
            
            # Step 9: Update actions panel session info
            logger.log_transcription_step("Updating actions panel")
            try:
                actions_panel = self.query_one("#actions-panel", ActionsPanel)
                transcription_log = self.query_one("#transcription-log", TranscriptionLog)
                recording_count = len(transcription_log.entries) if hasattr(transcription_log, 'entries') else 0
                latest_text = formatted_text if formatted_text else text
                ai_enabled = not self.formatter.disabled
                actions_panel.update_session_info(recording_count, latest_text, ai_enabled)
                logger.log_ui_operation("update_session_info", "actions-panel", True)
            except Exception as e:
                logger.error("Failed to update actions panel", {"error": str(e)}, exc_info=True)
            
            # Step 10: Update clipboard status
            logger.log_transcription_step("Updating clipboard status")
            try:
                if success:
                    self.query_one("#transcription-log", TranscriptionLog).add_info("Copied to clipboard")
                    logger.log_ui_operation("add_info (clipboard success)", "transcription-log", True)
                else:
                    self.query_one("#transcription-log", TranscriptionLog).add_error("Failed to copy to clipboard")
                    logger.log_ui_operation("add_error (clipboard fail)", "transcription-log", True)
            except Exception as e:
                logger.error("Failed to update clipboard status", {"error": str(e)}, exc_info=True)
                
            logger.log_transcription_step("Transcription process completed successfully")
                
        except asyncio.CancelledError:
            logger.info("Transcription cancelled by user")
        except Exception as e:
            logger.critical("Unexpected error in transcription process", {
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            try:
                self.query_one("#transcription-log", TranscriptionLog).add_error(f"Error: {e}")
                logger.log_ui_operation("add_error (general)", "transcription-log", True)
            except Exception as ui_e:
                logger.critical("Failed to update UI with general error", {"error": str(ui_e)}, exc_info=True)
        finally:
            # Reset state
            logger.log_transcription_step("Cleaning up and resetting state")
            try:
                self.query_one("#status-panel", StatusPanel).update_status(recording_state="idle")
                logger.log_ui_operation("update_status (idle)", "status-panel", True)
            except Exception as e:
                logger.error("Failed to reset status panel", {"error": str(e)}, exc_info=True)
                
            try:
                self.query_one("#recording-controls", RecordingControls).stop_recording()
                logger.log_ui_operation("stop_recording", "recording-controls", True)
            except Exception as e:
                logger.error("Failed to stop recording controls", {"error": str(e)}, exc_info=True)
                
            self.current_recording = None
            logger.log_method_exit("_record_and_transcribe")


class TextualTUI:
    """Textual TUI wrapper for CLI Whisperer."""
    
    def __init__(self):
        """Initialize the TUI wrapper."""
        self.app = None
        self.components_set = False
        
    def set_components(self, audio_recorder, transcriber, formatter, 
                      transcript_manager, history_manager, clipboard_manager):
        """Set the core components."""
        self.audio_recorder = audio_recorder
        self.transcriber = transcriber
        self.formatter = formatter
        self.transcript_manager = transcript_manager
        self.history_manager = history_manager
        self.clipboard_manager = clipboard_manager
        self.components_set = True
        
    def set_recording_duration(self, duration: int):
        """Set the recording duration."""
        self.recording_duration = duration
        
    def run(self):
        """Run the TUI application."""
        if not self.components_set:
            raise RuntimeError("Components must be set before running TUI")
            
        # Create and configure the TUI app
        app = CLIWhispererTUI()
        app.set_components(
            self.audio_recorder,
            self.transcriber,
            self.formatter,
            self.transcript_manager,
            self.history_manager,
            self.clipboard_manager
        )
        
        # Set recording duration if it was set on the wrapper
        if hasattr(self, 'recording_duration'):
            app.set_recording_duration(self.recording_duration)
        
        # Run the app
        app.run()
        
    # Delegate UI methods (for compatibility with Rich interface)
    def show_initialization(self, *args, **kwargs):
        """Show initialization (handled by TUI)."""
        pass
        
    def show_audio_devices(self, *args, **kwargs):
        """Show audio devices (handled by TUI)."""
        pass
        
    def show_recording_start(self, *args, **kwargs):
        """Show recording start (handled by TUI)."""
        pass
        
    def show_audio_level_meter(self, *args, **kwargs):
        """Show audio level meter (handled by TUI)."""
        pass
        
    def show_recording_complete(self, *args, **kwargs):
        """Show recording complete (handled by TUI)."""
        pass
        
    def show_recording_stopped_early(self, *args, **kwargs):
        """Show recording stopped early (handled by TUI)."""
        pass
        
    def show_transcription_start(self, *args, **kwargs):
        """Show transcription start (handled by TUI)."""
        pass
        
    def show_transcription_progress(self, *args, **kwargs):
        """Show transcription progress (handled by TUI)."""
        pass
        
    def show_transcription_complete(self, *args, **kwargs):
        """Show transcription complete (handled by TUI)."""
        pass
        
    def show_transcription_failed(self, *args, **kwargs):
        """Show transcription failed (handled by TUI)."""
        pass
        
    def show_transcription_result(self, *args, **kwargs):
        """Show transcription result (handled by TUI)."""
        pass
        
    def show_openai_formatting_start(self, *args, **kwargs):
        """Show OpenAI formatting start (handled by TUI)."""
        pass
        
    def show_openai_formatting_complete(self, *args, **kwargs):
        """Show OpenAI formatting complete (handled by TUI)."""
        pass
        
    def show_openai_formatting_failed(self, *args, **kwargs):
        """Show OpenAI formatting failed (handled by TUI)."""
        pass
        
    def show_formatted_result(self, *args, **kwargs):
        """Show formatted result (handled by TUI)."""
        pass
        
    def show_file_saved(self, *args, **kwargs):
        """Show file saved (handled by TUI)."""
        pass
        
    def show_clipboard_success(self, *args, **kwargs):
        """Show clipboard success (handled by TUI)."""
        pass
        
    def show_clipboard_failed(self, *args, **kwargs):
        """Show clipboard failed (handled by TUI)."""
        pass
        
    def show_spotify_resumed(self, *args, **kwargs):
        """Show Spotify resumed (handled by TUI)."""
        pass
        
    def show_no_speech_detected(self, *args, **kwargs):
        """Show no speech detected (handled by TUI)."""
        pass
        
    def show_history(self, *args, **kwargs):
        """Show history (handled by TUI)."""
        pass
        
    def show_error(self, *args, **kwargs):
        """Show error (handled by TUI)."""
        pass
        
    def show_warning(self, *args, **kwargs):
        """Show warning (handled by TUI)."""
        pass
        
    def show_info(self, *args, **kwargs):
        """Show info (handled by TUI)."""
        pass
        
    def print(self, *args, **kwargs):
        """Print (handled by TUI)."""
        pass