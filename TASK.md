# CLI Whisperer Refactoring Tasks

## Current Task: Refactor monolithic cli_whisperer.py into modular Python package
**Date Started**: 2025-07-10
**Status**: In Progress

### Task Description
Convert single 659-line script into professional Python package using uv with src/ layout. Maintain 100% backward compatibility while following CLAUDE.md conventions (max 500 lines per file, type hints, docstrings, etc.).

## Completed Tasks ✅
- [x] Create backup of original script (2025-07-10)
- [x] Initialize uv project structure (2025-07-10)
- [x] Create directory structure with core/, integrations/, utils/ (2025-07-10)
- [x] Configure pyproject.toml with dependencies and entry points (2025-07-10)
- [x] Create PLANNING.md documenting architecture (2025-07-10)
- [x] Create TASK.md for task tracking (2025-07-10)
- [x] Analyze existing cli_whisperer.py structure (2025-07-10)

## In Progress Tasks 🔄
- [ ] Extract core components following <500 lines rule
  - [ ] Extract TranscriptManager to src/cli_whisperer/core/file_manager.py
  - [ ] Extract audio recording logic to src/cli_whisperer/core/audio_recorder.py
  - [ ] Extract transcription logic to src/cli_whisperer/core/transcriber.py
  - [ ] Extract OpenAI formatting to src/cli_whisperer/core/formatter.py

## Pending Tasks 📋
- [ ] Extract integration components
  - [ ] Extract Spotify control to src/cli_whisperer/integrations/spotify_control.py
  - [ ] Extract clipboard operations to src/cli_whisperer/integrations/clipboard.py
  - [ ] Extract history management to src/cli_whisperer/utils/history.py
- [ ] Create configuration and main application
  - [ ] Create src/cli_whisperer/utils/config.py with constants
  - [ ] Create src/cli_whisperer/cli.py main application controller
  - [ ] Refactor src/cli_whisperer/main.py as clean entry point
  - [ ] Create all necessary __init__.py files
- [ ] Testing and validation
  - [ ] Create comprehensive pytest unit tests
  - [ ] Validate CLI interface remains identical
  - [ ] Test uv installation and CLI entry point
  - [ ] Run black formatting and linting
- [ ] Documentation
  - [ ] Update README.md with new structure

## Discovered During Work 🔍
- [x] Update AudioLevelMeter CSS for multi-line display support (2025-07-16)
  - Updated height from 3 to 5 in all 8 themes
  - Added line-height: 1.2 and padding: 0 1 for proper multi-line display
  - Updated compact status bar layouts to maintain consistency
  - Themes updated: EDM Synthwave, EDM Cyberpunk, EDM Trance, Marc Anthony, Professional, Dark Minimal, Neon Noir, Retro Wave
- [x] Implement comprehensive export functionality (2025-07-16)
  - Created ExportManager class with support for .txt, .md, .json, .csv, .docx, .pdf formats
  - Added export dialog UI with format selection and options
  - Implemented filtering and metadata inclusion options
  - Added export buttons to ActionsPanel for single, session, and history exports
  - Updated existing export actions to use new comprehensive system
  - Added CSS styles for export dialogs
  - Created unit tests for export functionality

## Quality Checkpoints 🎯
- [ ] All files under 500 lines (CLAUDE.md requirement)
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] CLI interface 100% identical
- [ ] All existing features working
- [ ] Tests covering core functionality
- [ ] Black formatting applied
- [ ] Package installs with uv

## Notes 📝
- Original script is 659 lines - need to split into ~7-8 modules
- Key classes identified: TranscriptManager, SimpleVoiceToText (needs splitting)
- Core dependencies: whisper, sounddevice, numpy, scipy, openai, pyperclip
- Critical: Spotify integration and clipboard functionality must be preserved