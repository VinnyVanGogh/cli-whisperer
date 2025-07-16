"""
User interface modules for CLI Whisperer.

This package provides different UI modes for the application:
- Rich output for single-run operations
- Textual TUI for continuous interactive sessions
"""

from .ui_manager import UIManager

__all__ = ["UIManager"]