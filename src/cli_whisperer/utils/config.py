"""
Configuration module containing constants and default settings.

This module centralizes all configuration constants used throughout
the CLI Whisperer application.
"""

from pathlib import Path

# Model configurations
DEFAULT_WHISPER_MODEL = "base"
DEFAULT_OPENAI_MODEL = "gpt-4.1-nano"

# Audio settings
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_RECORDING_DURATION = 120  # seconds
DEFAULT_BLOCKSIZE = 1024
MIN_RECORDING_LENGTH = 1.0  # seconds

# File management settings
DEFAULT_MAX_RECENT_FILES = 5
DEFAULT_CLEANUP_DAYS = 7
DEFAULT_HISTORY_ENTRIES = 50

def get_transcript_dir(tui_mode: bool = False) -> Path:
    """
    Get the appropriate transcript directory based on mode.
    
    Args:
        tui_mode (bool): Whether running in TUI mode.
        
    Returns:
        Path: Transcript directory path.
    """
    if tui_mode:
        # For TUI mode, use a dedicated directory in user's home
        tui_dir = Path.home() / ".cli-whisperer" / "transcripts"
        tui_dir.mkdir(parents=True, exist_ok=True)
        return tui_dir
    else:
        # For CLI mode, use current working directory
        return Path.cwd() / "transcripts"

# Default for backwards compatibility
DEFAULT_TRANSCRIPT_DIR = Path.cwd() / "transcripts"

# Audio visualization settings
LEVEL_METER_MULTIPLIER = 500
LEVEL_METER_MAX_BARS = 50

# Processing time estimation multipliers for different Whisper models
MODEL_MULTIPLIERS = {
    'tiny': 0.5,
    'base': 1.0,
    'small': 2.0,
    'medium': 5.0,
    'large': 10.0
}

# File extensions
RAW_TRANSCRIPT_EXTENSION = 'txt'
AI_TRANSCRIPT_EXTENSION = 'md'

# Warning thresholds
LONG_RECORDING_WARNING_SECONDS = 300  # 5 minutes