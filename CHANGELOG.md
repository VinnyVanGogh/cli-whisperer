# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-alpha.1] - 2025-07-16 (Alpha)

### Added | 2025-07-16 14:39:05

- feat: Add version command and update version info

- Update `__version__` to "1.0.0" in both `__init__.py` and `main.py`.

- Introduce `--version` CLI argument to display current version.

- Enhance argument parser with modern CLI options such as `--tui`, `--once`, `--format`, and related aliases.

- Implement logic to resolve conflicting formatting options (`--format` vs `--no-format`).

- Add support for selecting OpenAI models via `--openai-model` and `--ai-model` with proper precedence.

- Set environment variables for TUI theming and debugging when `--tui` is enabled.

- Improve code clarity and maintainability

### Files Changed (3) | 2025-07-16 14:39:05

- Modified: src/cli_whisperer/__init__.py
- Modified: src/cli_whisperer/main.py
- Untracked: .git_simplifier_backups/backup_20250716_143902.json

## [1.0.0-alpha.1] - 2025-07-16 (Alpha)

### Added | 2025-07-16 14:39:02

- added version command

### Files Changed (3) | 2025-07-16 14:39:02

- Modified: src/cli_whisperer/__init__.py
- Modified: src/cli_whisperer/main.py
- Untracked: .git_simplifier_backups/backup_20250716_143902.json

## [1.0.0] - 2025-07-16 (Release)

### Added | 2025-07-16 11:59:40

- fix: refine UI theme styling and layout for consistency and clarity

- Adjust multiple style definitions in `themes.py` to improve visual alignment and spacing

  - Replace `line-height: 1.2;` with `padding: 1;` on various components for uniform padding
  - Correct `align-items: center;` to `align: center middle;` in `textual_app.py` for proper alignment

- Enhance UI layout and appearance across different components, ensuring consistent spacing and alignment

- Simplify style declarations to improve maintainability and reduce potential rendering issues

### Files Changed (4) | 2025-07-16 11:59:40

- Modified: .gitignore
- Modified: src/cli_whisperer/ui/textual_app.py
- Modified: src/cli_whisperer/ui/themes.py
- Untracked: .git_simplifier_backups/backup_20250716_115935.json

## [1.0.0] - 2025-07-16 (Release)

### Test | 2025-07-16 11:59:36

- initial version working and tested

### Files Changed (4) | 2025-07-16 11:59:36

- Modified: .gitignore
- Modified: src/cli_whisperer/ui/textual_app.py
- Modified: src/cli_whisperer/ui/themes.py
- Untracked: .git_simplifier_backups/backup_20250716_115935.json
