"""
Theme system for CLI Whisperer TUI.

This module provides multiple theme options including EDM themes,
professional themes, and other visual styles.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Theme:
    """Theme configuration class."""
    name: str
    display_name: str
    description: str
    css: str
    colors: Dict[str, str]


class ThemeManager:
    """Manages theme switching and configuration."""
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_theme = "marc_anthony"
        self.themes = self._load_themes()
        
    def _load_themes(self) -> Dict[str, Theme]:
        """Load all available themes."""
        return {
            "edm_synthwave": self._create_edm_synthwave_theme(),
            "edm_cyberpunk": self._create_edm_cyberpunk_theme(),
            "edm_trance": self._create_edm_trance_theme(),
            "marc_anthony": self._create_marc_anthony_theme(),
            "professional": self._create_professional_theme(),
            "dark_minimal": self._create_dark_minimal_theme(),
            "neon_noir": self._create_neon_noir_theme(),
            "retro_wave": self._create_retro_wave_theme(),
        }
    
    def _create_edm_synthwave_theme(self) -> Theme:
        """Create EDM Synthwave theme (pink/cyan/retro)."""
        return Theme(
            name="edm_synthwave",
            display_name="EDM Synthwave",
            description="Retro 80s synthwave with hot pink and electric cyan",
            colors={
                "primary": "#FF00A0",      # Hot Pink
                "secondary": "#00F0FF",    # Electric Cyan
                "accent": "#FFDD00",       # Electric Yellow
                "background": "#0a0a0a",   # Near Black
                "surface": "#1a1a1a",      # Dark Gray
                "text": "#FFFFFF",         # White
                "text_muted": "#CCCCCC",   # Light Gray
            },
            css="""
/* EDM Synthwave Theme - Hot Pink & Electric Cyan */
Screen {
    background: #0a0a0a;
    color: #ffffff;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #1a0d2e;
    border: solid #FF00A0;
    border-title-color: #00F0FF;
    content-align: center middle;
    color: #ffffff;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #1a0d2e;
    border: solid #00F0FF;
    border-title-color: #FF00A0;
    content-align: center middle;
    color: #ffffff;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #16213e;
    border: solid #FFDD00;
    border-title-color: #FF00A0;
    color: #ffffff;
}

Button {
    background: #FF00A0;
    border: solid #00F0FF;
    color: #ffffff;
    text-style: bold;
}

Button:hover {
    background: #FF1493;
    border: solid #FFDD00;
}

TabbedContent {
    background: #1a1a1a;
    color: #ffffff;
}

TranscriptionLog {
    border: solid #00F0FF;
    border-title-color: #FF00A0;
    background: #1a1a1a;
    color: #ffffff;
}

HistoryViewer {
    border: solid #FF00A0;
    border-title-color: #00F0FF;
    background: #1a1a1a;
    color: #ffffff;
}

ActionsPanel {
    border: solid #FFDD00;
    border-title-color: #FF00A0;
    background: #1a1a1a;
    color: #ffffff;
}

.recording {
    background: #FF00A0;
    border: solid #00F0FF;
    color: #ffffff;
}

.transcribing {
    background: #FFDD00;
    border: solid #FF00A0;
    color: #000000;
}

.formatting {
    background: #00F0FF;
    border: solid #FF00A0;
    color: #000000;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #1a0d2e;
    border: solid #FF00A0;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #1a0d2e;
    border: solid #FF00A0;
    border-title-color: #00F0FF;
    color: #ffffff;
}

.preview-tabs > ContentSwitcher {
    background: #1a0d2e;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #1a0d2e;
    border: solid #FF00A0;
    color: #ffffff;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #FF00A0;
    border: solid #00F0FF;
    color: #000000;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #1a0d2e;
    color: #ffffff;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #FF00A0;
    border: solid #00F0FF;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #00F0FF;
    border: solid #FF00A0;
    color: #000000;
}

.spotify-btn:disabled {
    background: #333333;
    border: solid #666666;
    color: #999999;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #1a0d2e;
    border: solid #FF00A0;
    border-title-color: #00F0FF;
    color: #ffffff;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #1a0d2e;
    border: solid #FFDD00;
    border-title-color: #FF00A0;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #FF00A0;
    border: solid #00F0FF;
    color: #ffffff;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #FF1493;
    border: solid #FFDD00;
}

.preset-btn {
    background: #00F0FF;
    border: solid #FF00A0;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #1E90FF;
    border: solid #FFDD00;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #FF00A0;
}

.transcribing {
    border: solid #FF00A0;
}

.formatting {
    border: solid #FF00A0;
}
""")
    
    def _create_edm_cyberpunk_theme(self) -> Theme:
        """Create EDM Cyberpunk theme (electric blue/neon green)."""
        return Theme(
            name="edm_cyberpunk",
            display_name="EDM Cyberpunk",
            description="Futuristic cyberpunk with electric blue and neon green",
            colors={
                "primary": "#00F0FF",      # Electric Cyan
                "secondary": "#24FD36",    # Fluorescent Green
                "accent": "#FF1493",       # Deep Pink
                "background": "#000000",   # Pure Black
                "surface": "#1a1a1a",      # Dark Gray
                "text": "#FFFFFF",         # White
                "text_muted": "#00FFFF",   # Cyan
            },
            css="""
/* EDM Cyberpunk Theme - Electric Blue & Neon Green */
Screen {
    background: #000000;
    color: #ffffff;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #1a1a1a;
    border: solid #00F0FF;
    border-title-color: #24FD36;
    content-align: center middle;
    color: #ffffff;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #1a1a1a;
    border: solid #24FD36;
    border-title-color: #00F0FF;
    content-align: center middle;
    color: #ffffff;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #1a1a1a;
    border: solid #FF1493;
    border-title-color: #24FD36;
    color: #ffffff;
}

Button {
    background: #00F0FF;
    border: solid #24FD36;
    color: #000000;
    text-style: bold;
}

Button:hover {
    background: #24FD36;
    border: solid #FF1493;
    color: #ffffff;
}

TabbedContent {
    background: #1a1a1a;
    color: #ffffff;
}

TranscriptionLog {
    border: solid #24FD36;
    border-title-color: #00F0FF;
    background: #1a1a1a;
    color: #ffffff;
}

HistoryViewer {
    border: solid #00F0FF;
    border-title-color: #24FD36;
    background: #1a1a1a;
    color: #ffffff;
}

ActionsPanel {
    border: solid #FF1493;
    border-title-color: #00F0FF;
    background: #1a1a1a;
    color: #ffffff;
}

.recording {
    background: #FF1493;
    border: solid #24FD36;
    color: #ffffff;
}

.transcribing {
    background: #24FD36;
    border: solid #00F0FF;
    color: #000000;
}

.formatting {
    background: #00F0FF;
    border: solid #FF1493;
    color: #000000;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #1a1a1a;
    border: solid #00F0FF;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #1a1a1a;
    border: solid #00F0FF;
    border-title-color: #24FD36;
    color: #ffffff;
}

.preview-tabs > ContentSwitcher {
    background: #1a1a1a;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #1a1a1a;
    border: solid #00F0FF;
    color: #ffffff;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #00F0FF;
    border: solid #24FD36;
    color: #000000;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #1a1a1a;
    color: #ffffff;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #00F0FF;
    border: solid #24FD36;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #24FD36;
    border: solid #00F0FF;
    color: #ffffff;
}

.spotify-btn:disabled {
    background: #333333;
    border: solid #666666;
    color: #999999;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #1a1a1a;
    border: solid #00F0FF;
    border-title-color: #24FD36;
    color: #ffffff;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #1a1a1a;
    border: solid #FF1493;
    border-title-color: #24FD36;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #00F0FF;
    border: solid #24FD36;
    color: #000000;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #24FD36;
    border: solid #FF1493;
}

.preset-btn {
    background: #24FD36;
    border: solid #00F0FF;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #00FFBF;
    border: solid #FF1493;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #00F0FF;
}

.transcribing {
    border: solid #00F0FF;
}

.formatting {
    border: solid #00F0FF;
}
""")
    
    def _create_edm_trance_theme(self) -> Theme:
        """Create EDM Trance theme (deep blues/purples)."""
        return Theme(
            name="edm_trance",
            display_name="EDM Trance",
            description="Ethereal trance with deep blues and purples",
            colors={
                "primary": "#1E90FF",      # Dodger Blue
                "secondary": "#8A00C4",    # Purple
                "accent": "#FFFFFF",       # White
                "background": "#0a0a0a",   # Near Black
                "surface": "#1a1a1a",      # Dark Gray
                "text": "#FFFFFF",         # White
                "text_muted": "#CCCCCC",   # Light Gray
            },
            css="""
/* EDM Trance Theme - Deep Blues & Purples */
Screen {
    background: #0a0a0a;
    color: #ffffff;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #1a0d2e;
    border: solid #1E90FF;
    border-title-color: #8A00C4;
    content-align: center middle;
    color: #ffffff;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #1a0d2e;
    border: solid #8A00C4;
    border-title-color: #1E90FF;
    content-align: center middle;
    color: #ffffff;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #16213e;
    border: solid #FFFFFF;
    border-title-color: #8A00C4;
    color: #ffffff;
}

Button {
    background: #1E90FF;
    border: solid #8A00C4;
    color: #ffffff;
    text-style: bold;
}

Button:hover {
    background: #8A00C4;
    border: solid #1E90FF;
}

TabbedContent {
    background: #1a1a1a;
    color: #ffffff;
}

TranscriptionLog {
    border: solid #8A00C4;
    border-title-color: #1E90FF;
    background: #1a1a1a;
    color: #ffffff;
}

HistoryViewer {
    border: solid #1E90FF;
    border-title-color: #8A00C4;
    background: #1a1a1a;
    color: #ffffff;
}

ActionsPanel {
    border: solid #FFFFFF;
    border-title-color: #1E90FF;
    background: #1a1a1a;
    color: #ffffff;
}

.recording {
    background: #8A00C4;
    border: solid #1E90FF;
    color: #ffffff;
}

.transcribing {
    background: #1E90FF;
    border: solid #8A00C4;
    color: #ffffff;
}

.formatting {
    background: #FFFFFF;
    border: solid #1E90FF;
    color: #000000;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #1a0d2e;
    border: solid #1E90FF;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #1a0d2e;
    border: solid #1E90FF;
    border-title-color: #8A00C4;
    color: #ffffff;
}

.preview-tabs > ContentSwitcher {
    background: #1a0d2e;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #1a0d2e;
    border: solid #1E90FF;
    color: #ffffff;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #1E90FF;
    border: solid #8A00C4;
    color: #ffffff;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #1a0d2e;
    color: #ffffff;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #1E90FF;
    border: solid #8A00C4;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #8A00C4;
    border: solid #1E90FF;
    color: #ffffff;
}

.spotify-btn:disabled {
    background: #333333;
    border: solid #666666;
    color: #999999;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #1a0d2e;
    border: solid #1E90FF;
    border-title-color: #8A00C4;
    color: #ffffff;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #1a0d2e;
    border: solid #FFFFFF;
    border-title-color: #8A00C4;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #1E90FF;
    border: solid #8A00C4;
    color: #ffffff;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #8A00C4;
    border: solid #1E90FF;
}

.preset-btn {
    background: #8A00C4;
    border: solid #1E90FF;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #6B46C1;
    border: solid #FFFFFF;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #1E90FF;
}

.transcribing {
    border: solid #1E90FF;
}

.formatting {
    border: solid #1E90FF;
}
""")
    
    def _create_marc_anthony_theme(self) -> Theme:
        """Create Marc Anthony inspired metallic theme."""
        return Theme(
            name="marc_anthony",
            display_name="Marc Anthony Metallic",
            description="Sophisticated metallic theme with platinum, champagne, and rose gold",
            colors={
                "primary": "#8B9DC3",      # Platinum
                "secondary": "#F7E7CE",    # Champagne
                "accent": "#E8B4B8",       # Rose Gold
                "background": "#0F0F0F",   # Onyx Pure
                "surface": "#353839",      # Onyx Metallic
                "text": "#F8F8FF",         # Platinum Lightest
                "text_muted": "#D3D3D3",   # Platinum Medium
            },
            css="""
/* Marc Anthony Metallic Theme */
Screen {
    background: #0F0F0F;
    color: #F8F8FF;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #353839;
    border: solid #8B9DC3;
    border-title-color: #F7E7CE;
    content-align: center middle;
    color: #F8F8FF;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #353839;
    border: solid #F7E7CE;
    border-title-color: #8B9DC3;
    content-align: center middle;
    color: #F8F8FF;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #36454F;
    border: solid #E8B4B8;
    border-title-color: #F7E7CE;
    color: #F8F8FF;
}

Button {
    background: #8B9DC3;
    border: solid #F7E7CE;
    color: #000000;
    text-style: bold;
}

Button:hover {
    background: #F7E7CE;
    border: solid #8B9DC3;
}

TabbedContent {
    background: #353839;
    color: #F8F8FF;
}

TranscriptionLog {
    border: solid #F7E7CE;
    border-title-color: #8B9DC3;
    background: #353839;
    color: #F8F8FF;
}

HistoryViewer {
    border: solid #8B9DC3;
    border-title-color: #F7E7CE;
    background: #353839;
    color: #F8F8FF;
}

ActionsPanel {
    border: solid #E8B4B8;
    border-title-color: #8B9DC3;
    background: #353839;
    color: #F8F8FF;
}

.recording {
    background: #E8B4B8;
    border: solid #8B9DC3;
    color: #000000;
}

.transcribing {
    background: #F7E7CE;
    border: solid #E8B4B8;
    color: #000000;
}

.formatting {
    background: #8B9DC3;
    border: solid #F7E7CE;
    color: #F8F8FF;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #353839;
    border: solid #8B9DC3;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #353839;
    border: solid #8B9DC3;
    border-title-color: #F7E7CE;
    color: #F8F8FF;
}

.preview-tabs > ContentSwitcher {
    background: #353839;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #353839;
    border: solid #8B9DC3;
    color: #F8F8FF;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #8B9DC3;
    border: solid #F7E7CE;
    color: #000000;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #353839;
    color: #F8F8FF;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #8B9DC3;
    border: solid #F7E7CE;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #F7E7CE;
    border: solid #8B9DC3;
    color: #000000;
}

.spotify-btn:disabled {
    background: #333333;
    border: solid #666666;
    color: #999999;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #353839;
    border: solid #8B9DC3;
    border-title-color: #F7E7CE;
    color: #F8F8FF;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #353839;
    border: solid #E8B4B8;
    border-title-color: #F7E7CE;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #8B9DC3;
    border: solid #F7E7CE;
    color: #000000;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #F7E7CE;
    border: solid #8B9DC3;
}

.preset-btn {
    background: #F7E7CE;
    border: solid #8B9DC3;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #E8B4B8;
    border: solid #E8B4B8;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #8B9DC3;
}

.transcribing {
    border: solid #8B9DC3;
}

.formatting {
    border: solid #8B9DC3;
}
""")
    
    def _create_professional_theme(self) -> Theme:
        """Create professional/corporate theme."""
        return Theme(
            name="professional",
            display_name="Professional",
            description="Clean professional theme with subtle colors",
            colors={
                "primary": "#2563EB",      # Blue
                "secondary": "#6B7280",    # Gray
                "accent": "#10B981",       # Green
                "background": "#FFFFFF",   # White
                "surface": "#F9FAFB",      # Light Gray
                "text": "#111827",         # Dark Gray
                "text_muted": "#6B7280",   # Gray
            },
            css="""
/* Professional Theme */
Screen {
    background: #FFFFFF;
    color: #111827;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #F9FAFB;
    border: solid #2563EB;
    border-title-color: #6B7280;
    content-align: center middle;
    color: #111827;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #F9FAFB;
    border: solid #6B7280;
    border-title-color: #2563EB;
    content-align: center middle;
    color: #111827;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #F3F4F6;
    border: solid #10B981;
    border-title-color: #6B7280;
    color: #111827;
}

Button {
    background: #2563EB;
    border: solid #6B7280;
    color: #FFFFFF;
    text-style: bold;
}

Button:hover {
    background: #1D4ED8;
    border: solid #10B981;
}

TabbedContent {
    background: #F9FAFB;
    color: #111827;
}

TranscriptionLog {
    border: solid #6B7280;
    border-title-color: #2563EB;
    background: #F9FAFB;
    color: #111827;
}

HistoryViewer {
    border: solid #2563EB;
    border-title-color: #6B7280;
    background: #F9FAFB;
    color: #111827;
}

ActionsPanel {
    border: solid #10B981;
    border-title-color: #2563EB;
    background: #F9FAFB;
    color: #111827;
}

.recording {
    background: #EF4444;
    border: solid #2563EB;
    color: #FFFFFF;
}

.transcribing {
    background: #F59E0B;
    border: solid #6B7280;
    color: #FFFFFF;
}

.formatting {
    background: #10B981;
    border: solid #2563EB;
    color: #FFFFFF;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #F9FAFB;
    border: solid #2563EB;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #F9FAFB;
    border: solid #2563EB;
    border-title-color: #6B7280;
    color: #111827;
}

.preview-tabs > ContentSwitcher {
    background: #F9FAFB;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #F9FAFB;
    border: solid #2563EB;
    color: #111827;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #2563EB;
    border: solid #6B7280;
    color: #FFFFFF;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #F9FAFB;
    color: #111827;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #2563EB;
    border: solid #6B7280;
    color: #FFFFFF;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #1D4ED8;
    border: solid #2563EB;
    color: #FFFFFF;
}

.spotify-btn:disabled {
    background: #E5E7EB;
    border: solid #9CA3AF;
    color: #6B7280;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #F9FAFB;
    border: solid #2563EB;
    border-title-color: #6B7280;
    color: #111827;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #F9FAFB;
    border: solid #10B981;
    border-title-color: #6B7280;
    color: #111827;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #2563EB;
    border: solid #6B7280;
    color: #ffffff;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #1D4ED8;
    border: solid #10B981;
}

.preset-btn {
    background: #6B7280;
    border: solid #2563EB;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #4B5563;
    border: solid #10B981;
}

.presets-label {
    color: #111827;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #2563EB;
}

.transcribing {
    border: solid #2563EB;
}

.formatting {
    border: solid #2563EB;
}
""")
    
    def _create_dark_minimal_theme(self) -> Theme:
        """Create dark minimal theme."""
        return Theme(
            name="dark_minimal",
            display_name="Dark Minimal",
            description="Minimalist dark theme with subtle accents",
            colors={
                "primary": "#FFFFFF",      # White
                "secondary": "#6B7280",    # Gray
                "accent": "#3B82F6",       # Blue
                "background": "#111827",   # Dark Gray
                "surface": "#1F2937",      # Medium Dark Gray
                "text": "#F9FAFB",         # Light Gray
                "text_muted": "#9CA3AF",   # Medium Gray
            },
            css="""
/* Dark Minimal Theme */
Screen {
    background: #111827;
    color: #F9FAFB;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #1F2937;
    border: solid #FFFFFF;
    border-title-color: #6B7280;
    content-align: center middle;
    color: #F9FAFB;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #1F2937;
    border: solid #6B7280;
    border-title-color: #FFFFFF;
    content-align: center middle;
    color: #F9FAFB;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #374151;
    border: solid #3B82F6;
    border-title-color: #6B7280;
    color: #F9FAFB;
}

Button {
    background: #FFFFFF;
    border: solid #6B7280;
    color: #111827;
    text-style: bold;
}

Button:hover {
    background: #3B82F6;
    border: solid #FFFFFF;
    color: #FFFFFF;
}

TabbedContent {
    background: #1F2937;
    color: #F9FAFB;
}

TranscriptionLog {
    border: solid #6B7280;
    border-title-color: #FFFFFF;
    background: #1F2937;
    color: #F9FAFB;
}

HistoryViewer {
    border: solid #FFFFFF;
    border-title-color: #6B7280;
    background: #1F2937;
    color: #F9FAFB;
}

ActionsPanel {
    border: solid #3B82F6;
    border-title-color: #FFFFFF;
    background: #1F2937;
    color: #F9FAFB;
}

.recording {
    background: #EF4444;
    border: solid #FFFFFF;
    color: #FFFFFF;
}

.transcribing {
    background: #F59E0B;
    border: solid #6B7280;
    color: #FFFFFF;
}

.formatting {
    background: #3B82F6;
    border: solid #FFFFFF;
    color: #FFFFFF;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #1F2937;
    border: solid #FFFFFF;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #1F2937;
    border: solid #FFFFFF;
    border-title-color: #6B7280;
    color: #F9FAFB;
}

.preview-tabs > ContentSwitcher {
    background: #1F2937;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #1F2937;
    border: solid #FFFFFF;
    color: #F9FAFB;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #FFFFFF;
    border: solid #6B7280;
    color: #111827;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #1F2937;
    color: #F9FAFB;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #FFFFFF;
    border: solid #6B7280;
    color: #111827;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #3B82F6;
    border: solid #FFFFFF;
    color: #FFFFFF;
}

.spotify-btn:disabled {
    background: #374151;
    border: solid #4B5563;
    color: #6B7280;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #1F2937;
    border: solid #FFFFFF;
    border-title-color: #6B7280;
    color: #F9FAFB;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #1F2937;
    border: solid #3B82F6;
    border-title-color: #6B7280;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #FFFFFF;
    border: solid #6B7280;
    color: #111827;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #3B82F6;
    border: solid #FFFFFF;
}

.preset-btn {
    background: #6B7280;
    border: solid #FFFFFF;
    color: #ffffff;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #4B5563;
    border: solid #3B82F6;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #FFFFFF;
}

.transcribing {
    border: solid #FFFFFF;
}

.formatting {
    border: solid #FFFFFF;
}
""")
    
    def _create_neon_noir_theme(self) -> Theme:
        """Create neon noir theme."""
        return Theme(
            name="neon_noir",
            display_name="Neon Noir",
            description="Dark noir atmosphere with selective neon highlights",
            colors={
                "primary": "#FF0080",      # Neon Pink
                "secondary": "#00FFFF",    # Neon Cyan
                "accent": "#FFFF00",       # Neon Yellow
                "background": "#000000",   # Pure Black
                "surface": "#111111",      # Very Dark Gray
                "text": "#FFFFFF",         # White
                "text_muted": "#AAAAAA",   # Gray
            },
            css="""
/* Neon Noir Theme */
Screen {
    background: #000000;
    color: #ffffff;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #111111;
    border: solid #FF0080;
    border-title-color: #00FFFF;
    content-align: center middle;
    color: #ffffff;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #111111;
    border: solid #00FFFF;
    border-title-color: #FF0080;
    content-align: center middle;
    color: #ffffff;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #222222;
    border: solid #FFFF00;
    border-title-color: #00FFFF;
    color: #ffffff;
}

Button {
    background: #FF0080;
    border: solid #00FFFF;
    color: #000000;
    text-style: bold;
}

Button:hover {
    background: #00FFFF;
    border: solid #FFFF00;
    color: #000000;
}

TabbedContent {
    background: #111111;
    color: #ffffff;
}

TranscriptionLog {
    border: solid #00FFFF;
    border-title-color: #FF0080;
    background: #111111;
    color: #ffffff;
}

HistoryViewer {
    border: solid #FF0080;
    border-title-color: #00FFFF;
    background: #111111;
    color: #ffffff;
}

ActionsPanel {
    border: solid #FFFF00;
    border-title-color: #FF0080;
    background: #111111;
    color: #ffffff;
}

.recording {
    background: #FF0080;
    border: solid #00FFFF;
    color: #ffffff;
}

.transcribing {
    background: #FFFF00;
    border: solid #FF0080;
    color: #000000;
}

.formatting {
    background: #00FFFF;
    border: solid #FF0080;
    color: #000000;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #111111;
    border: solid #FF0080;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #111111;
    border: solid #FF0080;
    border-title-color: #00FFFF;
    color: #ffffff;
}

.preview-tabs > ContentSwitcher {
    background: #111111;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #111111;
    border: solid #FF0080;
    color: #ffffff;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #FF0080;
    border: solid #00FFFF;
    color: #000000;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #111111;
    color: #ffffff;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #FF0080;
    border: solid #00FFFF;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #00FFFF;
    border: solid #FFFF00;
    color: #000000;
}

.spotify-btn:disabled {
    background: #333333;
    border: solid #666666;
    color: #999999;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #111111;
    border: solid #FF0080;
    border-title-color: #00FFFF;
    color: #ffffff;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #111111;
    border: solid #FFFF00;
    border-title-color: #00FFFF;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #FF0080;
    border: solid #00FFFF;
    color: #000000;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #00FFFF;
    border: solid #FFFF00;
}

.preset-btn {
    background: #00FFFF;
    border: solid #FF0080;
    color: #000000;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #FFFF00;
    border: solid #FF0080;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #FF0080;
}

.transcribing {
    border: solid #FF0080;
}

.formatting {
    border: solid #FF0080;
}
""")
    
    def _create_retro_wave_theme(self) -> Theme:
        """Create retro wave theme."""
        return Theme(
            name="retro_wave",
            display_name="Retro Wave",
            description="80s retro wave with sunset gradients and grid patterns",
            colors={
                "primary": "#FF6B9D",      # Pink
                "secondary": "#A855F7",    # Purple
                "accent": "#F59E0B",       # Orange
                "background": "#1E1B4B",   # Dark Purple
                "surface": "#312E81",      # Medium Purple
                "text": "#FBBF24",         # Yellow
                "text_muted": "#FDE68A",   # Light Yellow
            },
            css="""
/* Retro Wave Theme */
Screen {
    background: #1E1B4B;
    color: #FBBF24;
}

StatusPanel {
    dock: top;
    height: 8;
    background: #312E81;
    border: solid #FF6B9D;
    border-title-color: #A855F7;
    content-align: center middle;
    color: #FBBF24;
    text-style: bold;
}

AudioLevelMeter {
    dock: top;
    height: 5;
    background: #312E81;
    border: solid #A855F7;
    border-title-color: #FF6B9D;
    content-align: center middle;
    color: #FBBF24;
    padding: 0 1;
}

RecordingControls {
    dock: top;
    height: 3;
    background: #3730A3;
    border: solid #F59E0B;
    border-title-color: #A855F7;
    color: #FBBF24;
}

Button {
    background: #FF6B9D;
    border: solid #A855F7;
    color: #1E1B4B;
    text-style: bold;
}

Button:hover {
    background: #A855F7;
    border: solid #F59E0B;
    color: #FBBF24;
}

TabbedContent {
    background: #312E81;
    color: #FBBF24;
}

TranscriptionLog {
    border: solid #A855F7;
    border-title-color: #FF6B9D;
    background: #312E81;
    color: #FBBF24;
}

HistoryViewer {
    border: solid #FF6B9D;
    border-title-color: #A855F7;
    background: #312E81;
    color: #FBBF24;
}

ActionsPanel {
    border: solid #F59E0B;
    border-title-color: #FF6B9D;
    background: #312E81;
    color: #FBBF24;
}

.recording {
    background: #FF6B9D;
    border: solid #A855F7;
    color: #1E1B4B;
}

.transcribing {
    background: #F59E0B;
    border: solid #FF6B9D;
    color: #1E1B4B;
}

.formatting {
    background: #A855F7;
    border: solid #F59E0B;
    color: #FBBF24;
}

/* Compact layout for smaller terminals */
.compact-status-bar {
    dock: top;
    height: 5;
    background: #312E81;
    border: solid #FF6B9D;
    layout: horizontal;
}

.compact-status-bar > StatusPanel {
    dock: none;
    height: 5;
    width: 1fr;
    border: none;
    margin: 0 1 0 0;
}

.compact-status-bar > AudioLevelMeter {
    dock: none;
    height: 5;
    width: 30;
    border: none;
    margin: 0 1 0 0;
    padding: 0 1;
}

.compact-status-bar > RecordingControls {
    dock: none;
    height: 5;
    width: 40;
    border: none;
    margin: 0;
}

.hidden {
    display: none;
}

/* Preview tabs styling */
.preview-tabs {
    background: #312E81;
    border: solid #FF6B9D;
    border-title-color: #A855F7;
    color: #FBBF24;
}

.preview-tabs > ContentSwitcher {
    background: #312E81;
    border: none;
    height: 3;
}

.preview-tabs > ContentSwitcher > Tab {
    background: #312E81;
    border: solid #FF6B9D;
    color: #FBBF24;
    text-style: bold;
    padding: 0 2;
}

.preview-tabs > ContentSwitcher > Tab.active {
    background: #FF6B9D;
    border: solid #A855F7;
    color: #1E1B4B;
    text-style: bold;
}

.preview-tabs TabPane {
    background: #312E81;
    color: #FBBF24;
    padding: 1;
}

/* Spotify Controls Styling */
.spotify-controls {
    layout: horizontal;
    align: center middle;
    height: 3;
    margin: 0 1;
    padding: 1;
}

.spotify-btn {
    background: #FF6B9D;
    border: solid #A855F7;
    color: #1E1B4B;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.spotify-btn:hover {
    background: #A855F7;
    border: solid #F59E0B;
    color: #FBBF24;
}

.spotify-btn:disabled {
    background: #4C1D95;
    border: solid #6B46C1;
    color: #9CA3AF;
}

SpotifyStatusPanel {
    dock: top;
    height: 12;
    background: #312E81;
    border: solid #FF6B9D;
    border-title-color: #A855F7;
    color: #FBBF24;
    padding: 1;
}

SpotifyStatusPanel > Static {
    text-align: center;
    margin: 0 1;
    height: 1;
}

SpotifyStatusPanel > .spotify-controls {
    dock: bottom;
    height: 3;
    margin: 1 0 0 0;
}

/* Recording Controls Styling */
RecordingControls {
    height: 8;
    background: #312E81;
    border: solid #F59E0B;
    border-title-color: #A855F7;
    color: #ffffff;
    padding: 1;
}

.recording-main-controls {
    dock: top;
    height: 3;
    layout: horizontal;
    margin: 0 0 1 0;
}

.duration-controls {
    dock: bottom;
    height: 3;
    layout: horizontal;
    align: center middle;
    margin: 0;
}

.duration-btn {
    background: #FF6B9D;
    border: solid #A855F7;
    color: #1E1B4B;
    text-style: bold;
    width: 6;
    height: 3;
    min-width: 6;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.duration-btn:hover {
    background: #A855F7;
    border: solid #F59E0B;
}

.preset-btn {
    background: #A855F7;
    border: solid #FF6B9D;
    color: #FBBF24;
    text-style: bold;
    width: 8;
    height: 3;
    min-width: 8;
    content-align: center middle;
    padding: 0;
    margin: 0 1;
}

.preset-btn:hover {
    background: #7C3AED;
    border: solid #F59E0B;
}

.presets-label {
    color: #ffffff;
    text-style: bold;
    margin: 0 1;
    content-align: center middle;
}

/* Visual State Indicators (Textual Compatible) */
.pulsing {
    border: solid #FF6B9D;
}

.transcribing {
    border: solid #FF6B9D;
}

.formatting {
    border: solid #FF6B9D;
}
""")
    
    def get_theme(self, theme_name: str) -> Theme:
        """Get a specific theme by name."""
        return self.themes.get(theme_name, self.themes["edm_synthwave"])
    
    def get_current_theme(self) -> Theme:
        """Get the current active theme."""
        return self.get_theme(self.current_theme)
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_theme_names(self) -> list[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def get_theme_display_names(self) -> list[str]:
        """Get list of theme display names."""
        return [theme.display_name for theme in self.themes.values()]
    
    def get_theme_list(self) -> list[tuple[str, str, str]]:
        """Get list of (name, display_name, description) tuples."""
        return [(name, theme.display_name, theme.description) 
                for name, theme in self.themes.items()]