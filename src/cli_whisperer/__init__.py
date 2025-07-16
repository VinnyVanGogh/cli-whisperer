"""
CLI Whisperer - Voice to Text Tool with Smart File Management.

A modular voice-to-text application that records audio, transcribes it using
OpenAI's Whisper model, optionally formats the text using OpenAI's chat models,
and manages transcript files with intelligent rotation and cleanup.
"""

from .cli import CLIApplication
from .main import main

__version__ = "0.1.0"
__all__ = ["CLIApplication", "main"]
