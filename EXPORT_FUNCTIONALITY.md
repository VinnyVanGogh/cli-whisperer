# Export Functionality Documentation

## Overview

The CLI Whisperer application includes comprehensive export functionality that allows users to export transcriptions in multiple formats with various options and filtering capabilities.

## Export Formats Supported

### Core Formats (Always Available)
- **TXT (.txt)** - Plain text format with optional metadata
- **Markdown (.md)** - Formatted markdown with headers and structure
- **JSON (.json)** - Structured data format with full metadata
- **CSV (.csv)** - Comma-separated values for spreadsheet compatibility

### Optional Formats (Require Additional Dependencies)
- **DOCX (.docx)** - Microsoft Word document format (requires `python-docx`)
- **PDF (.pdf)** - Portable Document Format (requires `reportlab`)

## Export Types

### 1. Single Transcription Export
- Exports the latest transcription from the current session
- Accessible via "Export Latest" button in Actions Panel
- Keyboard shortcut: `Ctrl+E`

### 2. Session Export
- Exports all transcriptions from the current session
- Accessible via "Export Session" button in Actions Panel
- Includes session metadata and numbering

### 3. History Export
- Exports historical transcriptions from the history database
- Accessible via "Export History" button in Actions Panel
- Keyboard shortcut: `Ctrl+Shift+E`
- Supports filtering by date range, working directory, and text search

## Export Options

### Content Options
- **Include Timestamps** - Add creation timestamps to exports
- **Include Metadata** - Include transcription metadata (model, duration, etc.)
- **Include Raw Text** - Include original transcription text
- **Include Formatted Text** - Include AI-formatted text (if available)
- **Include File Paths** - Include original file paths
- **Include Working Directory** - Include working directory information

### Filtering Options (History Export Only)
- **Date Range Filter** - Filter by creation date range
- **Working Directory Filter** - Filter by working directory path
- **Text Search Filter** - Filter by text content search

## Usage

### Using the TUI (Textual User Interface)

1. **Quick Export**
   - Click "Export Latest" for single transcription
   - Select format from quick format selection dialog
   - File is saved with default options

2. **Advanced Export**
   - Click "Export Session" or "Export History"
   - Configure format, options, and filters in dialog
   - Specify custom output location if needed
   - Click "Export" to save

3. **Keyboard Shortcuts**
   - `Ctrl+E` - Export latest transcription
   - `Ctrl+Shift+E` - Export all transcriptions

### Using the Command Line

The export functionality is integrated into the TUI and not directly accessible from the command line. Use the interactive TUI mode to access export features.

## File Structure

### Export Manager Components
- `src/cli_whisperer/utils/export_manager.py` - Main export logic
- `src/cli_whisperer/ui/export_dialog.py` - Export dialog UI components
- `tests/test_export_manager.py` - Unit tests for export functionality

### Integration Points
- `ActionsPanel` class - Export buttons and quick actions
- `CLIWhispererTUI` class - Export action handlers
- `TranscriptionLog` class - Session data access
- `HistoryManager` class - Historical data access

## Export Examples

### TXT Format Example
```
Timestamp: 2025-07-16T14:30:00

Raw Transcription:
This is a sample transcription from the CLI Whisperer application.

AI-Formatted Transcription:
# Sample Transcription

This is a **sample** transcription from the CLI Whisperer application.
```

### JSON Format Example
```json
{
  "timestamp": "2025-07-16T14:30:00",
  "raw_text": "This is a sample transcription from the CLI Whisperer application.",
  "formatted_text": "# Sample Transcription\n\nThis is a **sample** transcription from the CLI Whisperer application.",
  "metadata": {
    "model": "base",
    "duration": 5.0,
    "working_dir": "/home/user/project"
  }
}
```

### CSV Format Example
```csv
timestamp,raw_text,formatted_text
2025-07-16T14:30:00,"This is a sample transcription...","# Sample Transcription..."
2025-07-16T14:35:00,"Another transcription...","# Another Transcription..."
```

## Error Handling

The export functionality includes comprehensive error handling:

- **Format Validation** - Ensures selected format is supported
- **File System Errors** - Handles permission and disk space issues
- **Data Validation** - Validates export data before processing
- **User Feedback** - Provides clear success/error messages

## Dependencies

### Required (Core Formats)
- Python 3.8+
- `json` (built-in)
- `csv` (built-in)
- `pathlib` (built-in)

### Optional (Extended Formats)
- `python-docx` - For DOCX export support
- `reportlab` - For PDF export support

### Installation
```bash
# For DOCX support
pip install python-docx

# For PDF support
pip install reportlab

# For both
pip install python-docx reportlab
```

## Configuration

### Default Settings
- **Output Directory** - Same as transcript directory
- **File Naming** - Timestamp-based naming (`transcription_YYYYMMDD_HHMMSS.ext`)
- **Encoding** - UTF-8 for all text formats
- **Date Format** - ISO 8601 format (`YYYY-MM-DD HH:MM:SS`)

### Customization
Export options can be customized through the export dialog:
- Custom output locations
- Selective content inclusion/exclusion
- Custom filtering criteria
- Format-specific options

## Performance Considerations

- **Large Exports** - Progress feedback for large history exports
- **Memory Usage** - Efficient processing for large datasets
- **File Size** - Compression options for large exports (future enhancement)

## Future Enhancements

- **Batch Export** - Export multiple sessions at once
- **Cloud Storage** - Direct export to cloud storage services
- **Email Export** - Send exports via email
- **Template System** - Custom export templates
- **Compression** - ZIP archive support for large exports
- **Scheduling** - Automated export scheduling
- **API Integration** - Export to external services

## Troubleshooting

### Common Issues

1. **Export Failed Error**
   - Check file permissions in output directory
   - Ensure sufficient disk space
   - Verify format dependencies are installed

2. **Empty Export**
   - Check if transcriptions are available
   - Verify filter criteria aren't too restrictive
   - Ensure content options are properly selected

3. **Format Not Available**
   - Install required dependencies (`python-docx`, `reportlab`)
   - Restart application after installing dependencies

### Debug Information
- Export errors are logged with detailed error messages
- Use the "Show Statistics" button to verify available data
- Check the transcript directory for successful exports

## Contributing

When contributing to the export functionality:

1. **Add New Formats** - Implement in `ExportManager` class
2. **Add Export Options** - Extend `ExportOptions` class
3. **Add UI Components** - Update export dialog components
4. **Add Tests** - Create unit tests for new functionality
5. **Update Documentation** - Update this documentation

### Code Style
- Follow PEP 8 formatting
- Use type hints for all functions
- Add comprehensive docstrings
- Include error handling
- Write unit tests for new features