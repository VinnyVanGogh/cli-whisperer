# CLI Whisperer Project Architecture

## Overview
CLI Whisperer is a voice-to-text tool that records audio, transcribes it using OpenAI's Whisper model, optionally formats the text using OpenAI's chat models, and manages transcript files with intelligent rotation and cleanup.

## Project Goals
- **Modularity**: Refactor monolithic script into well-separated components
- **Maintainability**: Each module should be under 500 lines following CLAUDE.md conventions
- **Testability**: Components should be independently testable
- **Extensibility**: Easy to add new features and integrations
- **Backward Compatibility**: CLI interface must remain identical

## Architecture Style
- **Single Responsibility Principle**: Each class handles one specific concern
- **Separation of Concerns**: Core functionality, integrations, and utilities are separated
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Type Safety**: Full type hints throughout the codebase

## Module Structure

### Core Components (`src/cli_whisperer/core/`)
- **`file_manager.py`**: TranscriptManager for file operations and cleanup
- **`audio_recorder.py`**: AudioRecorder for microphone input and level monitoring
- **`transcriber.py`**: WhisperTranscriber for speech-to-text processing
- **`formatter.py`**: OpenAIFormatter for AI-powered text enhancement

### Integration Components (`src/cli_whisperer/integrations/`)
- **`spotify_control.py`**: SpotifyController for music playback management
- **`clipboard.py`**: ClipboardManager for system clipboard operations

### Utility Components (`src/cli_whisperer/utils/`)
- **`config.py`**: Configuration constants and settings
- **`history.py`**: HistoryManager for transcription history tracking

### Application Layer
- **`cli.py`**: CLIApplication orchestrating all components
- **`main.py`**: Entry point with argument parsing

## Design Constraints
- **File Size Limit**: Maximum 500 lines per file (CLAUDE.md requirement)
- **Type Hints**: All functions and classes must have type annotations
- **Docstrings**: Google-style docstrings for every function
- **Testing**: Pytest unit tests for all components
- **Code Quality**: Black formatting, PEP8 compliance

## File Size Allocation
- `file_manager.py`: ~150 lines (TranscriptManager)
- `audio_recorder.py`: ~150 lines (recording, device management, Spotify integration calls)
- `transcriber.py`: ~100 lines (Whisper model loading and transcription)
- `formatter.py`: ~80 lines (OpenAI formatting with threading)
- `spotify_control.py`: ~80 lines (Spotify status and control)
- `clipboard.py`: ~30 lines (clipboard operations)
- `history.py`: ~100 lines (history management and display)
- `config.py`: ~50 lines (constants and configuration)
- `cli.py`: ~200 lines (application orchestration)
- `main.py`: ~100 lines (argument parsing and setup)

## Dependencies
- **Core**: whisper, sounddevice, numpy, scipy
- **AI**: openai
- **Utilities**: pyperclip, pydantic, python-dotenv
- **Development**: pytest, black

## Testing Strategy
- **Unit Tests**: Each component tested independently with mocks
- **Integration Tests**: CLI workflows tested end-to-end
- **Regression Tests**: Ensure refactored version matches original behavior
- **Performance Tests**: Validate transcription speed and quality

## Migration Strategy
1. **Phase 1**: Project setup and core extraction
2. **Phase 2**: Integration component extraction
3. **Phase 3**: Application orchestration
4. **Phase 4**: Testing and validation
5. **Phase 5**: Documentation and cleanup

## Quality Gates
- All files under 500 lines
- Type checking passes (mypy)
- Code formatting passes (black)
- All tests pass
- CLI interface identical to original
- Performance within 5% of original