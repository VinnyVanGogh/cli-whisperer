# CLI Whisperer

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper-412991.svg?style=for-the-badge&logo=openai&logoColor=white)
![Textual](https://img.shields.io/badge/Textual-TUI-purple.svg?style=for-the-badge&logo=terminal&logoColor=white)
![Version](https://img.shields.io/badge/Version-0.2.5-green.svg?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-20/20_Passing-brightgreen.svg?style=for-the-badge)

A professional **voice-to-text** terminal user interface (TUI) application that combines the power of OpenAI's Whisper for speech recognition with GPT for intelligent text formatting. Features a modern, responsive interface with comprehensive export capabilities, Spotify integration, and advanced recording controls.

## Features

### Audio & Recording
- **High-quality audio recording** with configurable duration (15s - 5min+)
- **Real-time audio level meter** with waveform visualization
- **Adjustable recording controls** with preset duration buttons
- **Graceful recording management** with manual stop capability
- **Minimum recording length validation** for quality assurance

### AI-Powered Transcription
- **OpenAI Whisper integration** for accurate speech-to-text
- **Multiple Whisper model support** (tiny, base, small, medium, large)
- **Intelligent text formatting** with OpenAI GPT models
- **Dual transcription modes** - raw and AI-enhanced text
- **Comprehensive error handling** with fallback mechanisms

### Modern TUI Interface
- **8 professional themes** (EDM Synthwave, Cyberpunk, Marc Anthony, Professional, etc.)
- **Responsive design** optimized for all terminal sizes
- **Tabbed interface** with smooth navigation
- **Real-time status updates** and progress indicators
- **Pulse animations** and visual feedback systems

### Spotify Integration
- **Playback control** (play/pause, next/previous, shuffle, repeat)
- **Real-time status display** with track information
- **Interactive controls** directly in the TUI
- **Smart auto-pause** during recording sessions

### Advanced Export System
- **6 export formats**: TXT, Markdown, JSON, CSV, DOCX, PDF
- **Batch export capabilities** for all transcriptions
- **Filtering options** by date, directory, and text content
- **Metadata inclusion** with timestamps and file paths
- **Custom output locations** and file naming

### Comprehensive Keyboard Shortcuts
- **38 keyboard shortcuts** for all major functions
- **Power-user optimized** workflow
- **Intuitive key bindings** following standard conventions
- **Context-sensitive help** system

### File Management
- **Intelligent file organization** with automatic rotation
- **History tracking** with searchable database
- **Directory-aware storage** with working directory tracking
- **Automatic cleanup** of old files
- **Backup and recovery** systems

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Configuration](#configuration)
- [Export Functionality](#export-functionality)
- [Themes](#themes)
- [Development](#development)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- **Python 3.10+** (required for OpenAI Whisper compatibility)
- **pip** or **uv** package manager
- **OpenAI API key** (optional, for text formatting)
- **Microphone** access for recording
- **Spotify CLI** (optional, for music integration)

### Quick Install with UV (Recommended)

```bash
# Install with UV (fastest method)
uv pip install -e .

# Or install from source
git clone https://github.com/VinnyVanGogh/cli-whisperer.git
cd cli-whisperer
uv pip install -e .
```

### Install with Pip

```bash
# Clone the repository
git clone https://github.com/VinnyVanGogh/cli-whisperer.git
cd cli-whisperer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### System Dependencies

```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# Windows
# Install Visual Studio Build Tools
# PortAudio will be installed automatically
```

## Quick Start

### 1. Basic Recording

```bash
# Start CLI Whisperer
cli-whisperer

# Record for 2 minutes with OpenAI formatting
cli-whisperer --duration 120 --format

# Record once and exit
cli-whisperer --once
```

### 2. TUI Mode

```bash
# Launch the interactive TUI
cli-whisperer --tui

# TUI with specific theme
cli-whisperer --tui --theme professional
```

### 3. Configuration

```bash
# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Configure output directory
cli-whisperer --output-dir ~/Documents/transcripts
```

## Usage

### Command Line Interface

```bash
cli-whisperer [OPTIONS]

Options:
  --tui                   Launch interactive TUI mode
  --once                  Record once and exit
  -d, --duration SECONDS  Recording duration (default: 120)
  -min, --minutes MIN     Recording duration in minutes
  --format                Enable OpenAI text formatting
  --no-format             Disable OpenAI text formatting
  --model MODEL           Whisper model (tiny/base/small/medium/large)
  --openai-model MODEL    OpenAI model for formatting
  --theme THEME           TUI theme selection
  --output-dir PATH       Custom output directory
  --cleanup-days DAYS     Days to keep old files (default: 7)
  --debug                 Enable debug logging
  --help                  Show help message
```

### TUI Mode Features

#### Recording Controls
- **Record Button**: Start recording session
- **Stop Button**: End recording early
- **Duration Controls**: Adjust recording time (±15s increments)
- **Preset Buttons**: Quick duration selection (30s, 1m, 2m, 5m)

#### Real-time Feedback
- **Audio Level Meter**: Visual waveform with color coding
- **Progress Bar**: Recording countdown with time remaining
- **Status Panel**: Current mode and session information

#### Text Management
- **Tabbed Previews**: Switch between raw and AI-formatted text
- **Copy Functions**: One-click copying to clipboard
- **Edit Integration**: Direct Neovim editing support

## Keyboard Shortcuts

### Core Actions
| Key | Action | Description |
|-----|--------|-------------|
| `R` | Record | Start recording |
| `S` | Stop | Stop recording |
| `Space` | Toggle Recording | Start/stop recording |
| `Q` / `Escape` | Quit | Exit application |

### Navigation
| Key | Action | Description |
|-----|--------|-------------|
| `Tab` / `Shift+Tab` | Navigate Tabs | Switch between tabs |
| `H` | History | Show history tab |
| `T` | Themes | Show themes tab |
| `F1` / `?` | Help | Show help dialog |

### Duration Controls
| Key | Action | Description |
|-----|--------|-------------|
| `+` / `-` | Adjust Duration | Increase/decrease by 15s |
| `1` - `4` | Duration Presets | Set 30s, 1m, 2m, 5m |

### Copy Operations
| Key | Action | Description |
|-----|--------|-------------|
| `C` | Copy AI Text | Copy formatted transcription |
| `Ctrl+C` | Copy Raw Text | Copy original transcription |
| `Ctrl+A` | Enhanced Copy | Copy with preview |
| `Ctrl+Shift+A` | Copy All | Copy all transcriptions |

### Spotify Controls
| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+P` | Play/Pause | Toggle playback |
| `Ctrl+N` / `Ctrl+B` | Next/Previous | Track navigation |
| `Ctrl+S` | Toggle Panel | Show/hide Spotify panel |
| `Ctrl+Shift+S` | Shuffle | Toggle shuffle mode |
| `Ctrl+Shift+R` | Repeat | Toggle repeat mode |

### File Operations
| Key | Action | Description |
|-----|--------|-------------|
| `Ctrl+E` | Export | Export current transcription |
| `Ctrl+Shift+E` | Export All | Export all transcriptions |
| `Ctrl+O` | Open Directory | Open transcript folder |
| `Ctrl+D` | Clean Files | Delete old files |

### Advanced Features
| Key | Action | Description |
|-----|--------|-------------|
| `F2` | Toggle Debug | Enable/disable debug mode |
| `F3` | Toggle Audio Meter | Show/hide audio meter |
| `F4` | Compact Mode | Toggle compact layout |
| `F5` | Refresh | Refresh interface |
| `Ctrl+R` | Reload Config | Reload configuration |
| `Ctrl+Shift+T` | Switch Theme | Cycle through themes |

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY="sk-your-api-key-here"
export OPENAI_MODEL="gpt-4"

# Application Settings
export CLI_WHISPERER_OUTPUT_DIR="~/Documents/transcripts"
export CLI_WHISPERER_THEME="professional"
export CLI_WHISPERER_DEBUG="false"

# Recording Settings
export CLI_WHISPERER_DURATION="120"
export CLI_WHISPERER_MODEL="base"
export CLI_WHISPERER_MIN_LENGTH="1.0"
```

### Configuration Files

The application uses the following configuration structure:

```
~/.config/cli-whisperer/
├── config.yaml          # Main configuration
├── themes/              # Custom themes
│   ├── custom.css
│   └── user-theme.css
└── history/             # History database
    ├── history.json
    └── backups/
```

### Custom Themes

Create custom themes by extending the base theme system:

```css
/* ~/.config/cli-whisperer/themes/custom.css */
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    --accent-color: #your-color;
    --background-color: #your-color;
}

RecordingControls {
    background: var(--background-color);
    border: solid var(--primary-color);
}
```

## Export Functionality

### Supported Formats

| Format | Extension | Description | Metadata |
|--------|-----------|-------------|----------|
| **Plain Text** | `.txt` | Simple text format | Optional |
| **Markdown** | `.md` | Formatted with headers | Full |
| **JSON** | `.json` | Structured data | Complete |
| **CSV** | `.csv` | Spreadsheet compatible | Basic |
| **Word Document** | `.docx` | Microsoft Word | Full |
| **PDF** | `.pdf` | Portable document | Complete |

### Export Options

#### Content Selection
- **Raw transcription text**
- **AI-formatted text**
- **Timestamps and metadata**
- **File paths and working directory**
- **Recording duration and model info**

#### Filtering (History Export)
- **Date Range**: Export transcriptions from specific time periods
- **Directory Filter**: Export only from specific working directories
- **Text Search**: Export transcriptions containing specific keywords
- **Model Filter**: Export by Whisper model used

#### Export Types

```bash
# Export latest transcription
Ctrl+E  # Interactive format selection

# Export current session
# Use Export Session button in Actions Panel

# Export filtered history
Ctrl+Shift+E  # Full export dialog with filtering
```

## Themes

### Built-in Themes

| Theme | Description | Colors |
|-------|-------------|---------|
| **EDM Synthwave** | Retro neon aesthetic | Hot pink, electric cyan, yellow |
| **EDM Cyberpunk** | Futuristic dark theme | Cyan, green, deep pink |
| **EDM Trance** | Clean electronic look | Blue, purple, white |
| **Marc Anthony** | Elegant gold theme | Platinum, champagne, rose gold |
| **Professional** | Business-friendly | Blue, gray, green |
| **Dark Minimal** | Clean dark interface | White, gray, blue |
| **Neon Noir** | High contrast neon | Pink, cyan, yellow |
| **Retro Wave** | 80s inspired | Pink, purple, orange |

### Theme Switching

```bash
# Command line
cli-whisperer --tui --theme professional

# In TUI
T                    # Open themes tab
Ctrl+Shift+T        # Quick theme cycle
```

## Development

### Project Structure

```
cli-whisperer/
├── src/cli_whisperer/
│   ├── core/                 # Core functionality
│   │   ├── audio_recorder.py # Audio recording and processing
│   │   ├── transcriber.py    # Whisper integration
│   │   ├── formatter.py      # OpenAI text formatting
│   │   └── file_manager.py   # File operations
│   ├── integrations/         # External integrations
│   │   ├── spotify_control.py # Spotify API integration
│   │   └── clipboard.py      # System clipboard
│   ├── ui/                   # User interface
│   │   ├── textual_app.py    # Main TUI application
│   │   ├── themes.py         # Theme system
│   │   ├── export_dialog.py  # Export dialogs
│   │   └── edit_manager.py   # Neovim integration
│   ├── utils/                # Utilities
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging system
│   │   ├── history.py        # History management
│   │   └── export_manager.py # Export functionality
│   ├── cli.py                # CLI interface
│   └── main.py               # Entry point
├── tests/                    # Test suite
│   ├── test_export_manager.py
│   └── ...
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/VinnyVanGogh/cli-whisperer.git
cd cli-whisperer

# Create development environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/cli_whisperer

# Run specific test file
pytest tests/test_export_manager.py

# Run tests with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/cli_whisperer

# Linting
flake8 src/ tests/

# Run all quality checks
pre-commit run --all-files
```

## API Reference

### Core Classes

#### `CLIApplication`
Main application orchestrator that coordinates all components.

```python
from cli_whisperer.cli import CLIApplication

app = CLIApplication(
    duration=120,
    format_enabled=True,
    model="base",
    output_dir="./transcripts"
)
app.run()
```

#### `AudioRecorder`
Handles audio recording with real-time level monitoring.

```python
from cli_whisperer.core.audio_recorder import AudioRecorder

recorder = AudioRecorder(
    duration=60,
    sample_rate=16000,
    channels=1
)
audio_data = recorder.record()
```

#### `WhisperTranscriber`
Manages Whisper model loading and transcription.

```python
from cli_whisperer.core.transcriber import WhisperTranscriber

transcriber = WhisperTranscriber(model="base")
text = transcriber.transcribe(audio_data)
```

#### `ExportManager`
Handles multi-format export functionality.

```python
from cli_whisperer.utils.export_manager import ExportManager, ExportFormat

manager = ExportManager()
manager.export_transcription(
    text="Hello world",
    format=ExportFormat.MARKDOWN,
    output_path="output.md"
)
```

### Integration Points

#### Spotify Integration
```python
from cli_whisperer.integrations.spotify_control import SpotifyController

spotify = SpotifyController()
if spotify.is_available():
    spotify.play()
    status = spotify.get_status()
```

#### Theme System
```python
from cli_whisperer.ui.themes import ThemeManager

theme_manager = ThemeManager()
theme_manager.set_theme("professional")
css = theme_manager.get_current_theme().css
```

## Troubleshooting

### Common Issues

#### Audio Recording Problems
```bash
# Check microphone permissions
# macOS: System Preferences > Security & Privacy > Microphone
# Linux: Check PulseAudio/ALSA configuration

# Test audio recording
python -c "import sounddevice as sd; print(sd.query_devices())"
```

#### OpenAI API Issues
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API connection
python -c "import openai; print(openai.models.list())"
```

#### Whisper Model Loading
```bash
# Clear model cache
rm -rf ~/.cache/whisper

# Download specific model
python -c "import whisper; whisper.load_model('base')"
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
# Command line
cli-whisperer --debug

# Environment variable
export CLI_WHISPERER_DEBUG=true

# In TUI
F2  # Toggle debug mode
```

### Performance Optimization

#### For Low-End Systems
```bash
# Use smaller Whisper model
cli-whisperer --model tiny

# Reduce recording duration
cli-whisperer --duration 30

# Disable OpenAI formatting
cli-whisperer --no-format
```

#### For High-End Systems
```bash
# Use larger Whisper model
cli-whisperer --model large

# Enable all features
cli-whisperer --format --tui --theme professional
```

### Log Files

Check log files for detailed error information:

```bash
# Application logs
tail -f ~/.local/share/cli-whisperer/logs/cli-whisperer.log

# Debug logs (when debug mode enabled)
tail -f ~/.local/share/cli-whisperer/logs/debug.log
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Process

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following the code style guidelines
4. **Add tests** for your changes
5. **Ensure all tests pass** (`pytest`)
6. **Update documentation** if needed
7. **Commit your changes** (`git commit -m 'Add amazing feature'`)
8. **Push to the branch** (`git push origin feature/amazing-feature`)
9. **Open a Pull Request**

### Code Style Guidelines

- **Follow PEP 8** Python style guide
- **Use type hints** for all functions and methods
- **Write docstrings** in Google style
- **Keep functions under 50 lines** when possible
- **Maintain test coverage** above 90%

### Issue Reports

When reporting issues, please include:

- **Python version** and operating system
- **Complete error messages** and stack traces
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Log files** if applicable

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI** for the Whisper and GPT models
- **Textual** for the excellent TUI framework
- **Python Community** for the amazing ecosystem
- **All contributors** who have helped improve this project

## Support

- Email: [133192356+VinnyVanGogh@users.noreply.github.com]
- Issues: [GitHub Issues](https://github.com/VinnyVanGogh/cli-whisperer/issues)
- Documentation: [Project Wiki](https://github.com/VinnyVanGogh/cli-whisperer/wiki)

---

**Made with ❤️ by VinnyVanGogh**  
*Transforming voice to text with style and intelligence*

[⬆️ Back to Top](#cli-whisperer)