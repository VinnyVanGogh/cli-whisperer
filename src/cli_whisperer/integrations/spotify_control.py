"""
Spotify integration module for controlling music playback.

This module provides the SpotifyController class which interfaces with
the Spotify API directly, providing rich status information and control.
"""

import subprocess
import sys
import time
from typing import Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class SpotifyController:
    """Handles Spotify playback control during recording sessions."""
    
    def __init__(self):
        """Initialize the Spotify controller."""
        self.console = Console()
        self.animation_settings = {
            "show_animations": True,
            "animation_duration": 0.2,
            "processing_message": "Processing",
            "steps": 101,
        }
        
    def spotify_command(self, command: str, *args) -> subprocess.CompletedProcess:
        """
        Execute a Spotify command using the spotify CLI.
        
        Args:
            command (str): The Spotify command to execute.
            *args: Additional arguments for the command.
            
        Returns:
            subprocess.CompletedProcess: The result of the command execution.
        """
        cmd = ["spotify", command] + list(args)
        result = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        return result
    
    def check_playing(self) -> bool:
        """
        Check if Spotify is currently playing.

        Returns:
            bool: True if Spotify is playing, False otherwise.
        """
        try:
            result = self.spotify_command("status")
            if result.returncode == 0 and result.stdout:
                # Check if output contains "Spotify is currently playing"
                return "Spotify is currently playing" in result.stdout
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # spotify command not found or timed out
            return False
        except Exception as e:
            print(f"⚠️  Failed to check Spotify status: {e}")
            return False
    
    def pause(self) -> bool:
        """
        Pause Spotify playback.

        Returns:
            bool: True if pause command succeeded, False otherwise.
        """
        try:
            result = self.spotify_command("pause")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to pause Spotify: {e}")
            return False
    
    def play(self) -> bool:
        """
        Resume Spotify playback.

        Returns:
            bool: True if play command succeeded, False otherwise.
        """
        try:
            result = self.spotify_command("play")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to resume Spotify: {e}")
            return False
            
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed Spotify status information.
        
        Returns:
            Optional[Dict[str, Any]]: Status information or None if failed.
        """
        try:
            result = self.spotify_command("status")
            if result.returncode == 0 and result.stdout:
                return self._parse_status_output(result.stdout)
            return None
        except Exception as e:
            print(f"⚠️  Failed to get Spotify status: {e}")
            return None
            
    def _parse_status_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Spotify status output into a structured dictionary.
        
        Args:
            output (str): Raw status output from Spotify command.
            
        Returns:
            Dict[str, Any]: Parsed status information.
        """
        status = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            if "Artist:" in line:
                status['artist'] = line.split("Artist:")[1].strip()
            elif "Album:" in line:
                status['album'] = line.split("Album:")[1].strip()
            elif "Track:" in line:
                status['track'] = line.split("Track:")[1].strip()
            elif "Position:" in line:
                status['position'] = line.split("Position:")[1].strip()
            elif "Repeat:" in line:
                status['repeat'] = line.split("Repeat:")[1].strip()
            elif "Shuffle:" in line:
                status['shuffle'] = line.split("Shuffle:")[1].strip()
            elif "Spotify is currently playing" in line:
                status['playing'] = True
            elif "Spotify is currently paused" in line:
                status['playing'] = False
                
        return status
        
    def display_status(self) -> None:
        """Display formatted Spotify status."""
        status = self.get_status()
        if not status:
            self.console.print("[yellow]No Spotify status available[/yellow]")
            return
            
        # Create a stylized panel for status
        status_text = Text()
        
        if status.get('artist'):
            status_text.append("\n🎤 Artist: ", style="bold green")
            status_text.append(status['artist'], style="green")
            
        if status.get('album'):
            status_text.append("\n💿 Album: ", style="bold cyan")
            status_text.append(status['album'], style="cyan")
            
        if status.get('track'):
            status_text.append("\n🎵 Track: ", style="bold magenta")
            status_text.append(status['track'], style="magenta")
            
        if status.get('position'):
            status_text.append("\n⏱️ Position: ", style="bold")
            status_text.append(status['position'])
            
        if status.get('repeat'):
            status_text.append("\n🔁 Repeat: ", style="bold yellow")
            status_text.append(status['repeat'], style="yellow")
            
        if status.get('shuffle'):
            status_text.append("\n🔀 Shuffle: ", style="bold blue")
            status_text.append(status['shuffle'], style="blue")
            
        playing_status = "▶️ Playing" if status.get('playing') else "⏸️ Paused"
        status_text.append(f"\n{playing_status}", style="bold white")
        
        self.console.print(
            Panel(status_text, title="🎧 Spotify Status", border_style="bright_green")
        )
        
    def next_track(self) -> bool:
        """Skip to next track."""
        try:
            result = self.spotify_command("next")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to skip to next track: {e}")
            return False
            
    def previous_track(self) -> bool:
        """Go to previous track."""
        try:
            result = self.spotify_command("prev")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to go to previous track: {e}")
            return False
            
    def toggle_shuffle(self) -> bool:
        """Toggle shuffle mode."""
        try:
            result = self.spotify_command("toggle", "shuffle")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to toggle shuffle: {e}")
            return False
            
    def toggle_repeat(self) -> bool:
        """Toggle repeat mode."""
        try:
            result = self.spotify_command("toggle", "repeat")
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Failed to toggle repeat: {e}")
            return False