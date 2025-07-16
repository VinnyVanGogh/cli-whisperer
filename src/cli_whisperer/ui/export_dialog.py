"""
Export dialog for the CLI Whisperer TUI application.

This module provides export dialog components for selecting formats,
options, and destinations for transcription exports.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from ..utils.export_manager import ExportFormat, ExportOptions


class ExportDialog(ModalScreen):
    """Modal dialog for export configuration."""
    
    def __init__(self, export_type: str = "single", **kwargs):
        """
        Initialize the export dialog.
        
        Args:
            export_type (str): Type of export - "single", "session", or "history"
        """
        super().__init__(**kwargs)
        self.export_type = export_type
        self.result = None
        
    def compose(self) -> ComposeResult:
        """Compose the export dialog."""
        with Container(classes="export-dialog"):
            with Vertical(classes="export-content"):
                # Header
                yield Static(f"[bold blue]Export {self.export_type.title()} Transcription(s)[/bold blue]", 
                           classes="export-header")
                
                # Format selection
                with Horizontal(classes="export-row"):
                    yield Label("Format:", classes="export-label")
                    yield Select(
                        [
                            ("Plain Text (.txt)", ExportFormat.TXT),
                            ("Markdown (.md)", ExportFormat.MD),
                            ("JSON (.json)", ExportFormat.JSON),
                            ("CSV (.csv)", ExportFormat.CSV),
                            ("Word Document (.docx)", ExportFormat.DOCX),
                            ("PDF (.pdf)", ExportFormat.PDF),
                        ],
                        id="format-select",
                        classes="export-select"
                    )
                
                # Output location
                with Horizontal(classes="export-row"):
                    yield Label("Output:", classes="export-label")
                    yield Input(
                        placeholder="Leave empty for default location",
                        id="output-path",
                        classes="export-input"
                    )
                    yield Button("Browse", id="browse-button", variant="default", classes="export-button")
                
                # Export options
                yield Static("[bold]Export Options[/bold]", classes="export-section-header")
                
                with Horizontal(classes="export-row"):
                    yield Checkbox("Include timestamps", id="include-timestamps", value=True)
                    yield Checkbox("Include metadata", id="include-metadata", value=True)
                    
                with Horizontal(classes="export-row"):
                    yield Checkbox("Include raw text", id="include-raw", value=True)
                    yield Checkbox("Include formatted text", id="include-formatted", value=True)
                    
                with Horizontal(classes="export-row"):
                    yield Checkbox("Include file paths", id="include-paths", value=False)
                    yield Checkbox("Include working directory", id="include-workdir", value=False)
                
                # Filter options (only for history exports)
                if self.export_type == "history":
                    yield Static("[bold]Filter Options[/bold]", classes="export-section-header")
                    
                    with Horizontal(classes="export-row"):
                        yield Label("Working Directory:", classes="export-label")
                        yield Input(
                            placeholder="Filter by working directory",
                            id="filter-workdir",
                            classes="export-input"
                        )
                        
                    with Horizontal(classes="export-row"):
                        yield Label("Text Search:", classes="export-label")
                        yield Input(
                            placeholder="Search in transcription text",
                            id="filter-text",
                            classes="export-input"
                        )
                
                # Buttons
                with Horizontal(classes="export-buttons"):
                    yield Button("Cancel", id="cancel-button", variant="default")
                    yield Button("Export", id="export-button", variant="primary")
                    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.dismiss(None)
        elif event.button.id == "export-button":
            self._handle_export()
        elif event.button.id == "browse-button":
            self._browse_output_location()
            
    def _handle_export(self) -> None:
        """Handle export button press."""
        try:
            # Get format selection
            format_select = self.query_one("#format-select", Select)
            selected_format = format_select.value
            
            # Get output path
            output_input = self.query_one("#output-path", Input)
            output_path = output_input.value.strip() if output_input.value else None
            
            # Get export options
            options = ExportOptions(
                include_timestamps=self.query_one("#include-timestamps", Checkbox).value,
                include_metadata=self.query_one("#include-metadata", Checkbox).value,
                include_raw_text=self.query_one("#include-raw", Checkbox).value,
                include_formatted_text=self.query_one("#include-formatted", Checkbox).value,
                include_file_paths=self.query_one("#include-paths", Checkbox).value,
                include_working_dir=self.query_one("#include-workdir", Checkbox).value,
            )
            
            # Get filter options for history exports
            filter_criteria = None
            if self.export_type == "history":
                filter_workdir = self.query_one("#filter-workdir", Input).value.strip()
                filter_text = self.query_one("#filter-text", Input).value.strip()
                
                if filter_workdir or filter_text:
                    filter_criteria = {}
                    if filter_workdir:
                        filter_criteria['working_dir'] = filter_workdir
                    if filter_text:
                        filter_criteria['text_search'] = filter_text
            
            # Prepare result
            result = {
                'format': selected_format,
                'output_path': Path(output_path) if output_path else None,
                'options': options,
                'filter_criteria': filter_criteria
            }
            
            self.dismiss(result)
            
        except Exception as e:
            self.app.notify(f"❌ Export configuration error: {e}", severity="error")
            
    def _browse_output_location(self) -> None:
        """Browse for output location."""
        # This would typically open a file dialog
        # For now, we'll just provide a placeholder
        self.app.notify("💡 File browser not implemented yet. Enter path manually.", severity="information")


class ExportOptionsScreen(ModalScreen):
    """Simple screen for quick export options."""
    
    def __init__(self, formats: List[str], **kwargs):
        """
        Initialize the export options screen.
        
        Args:
            formats (List[str]): List of available formats
        """
        super().__init__(**kwargs)
        self.formats = formats
        
    def compose(self) -> ComposeResult:
        """Compose the export options screen."""
        with Container(classes="export-options-dialog"):
            with Vertical(classes="export-options-content"):
                yield Static("[bold blue]Quick Export[/bold blue]", classes="export-header")
                
                yield Static("Select format:", classes="export-label")
                
                # Format buttons
                with Vertical(classes="format-buttons"):
                    for fmt in self.formats:
                        format_name = {
                            ExportFormat.TXT: "Plain Text (.txt)",
                            ExportFormat.MD: "Markdown (.md)",
                            ExportFormat.JSON: "JSON (.json)",
                            ExportFormat.CSV: "CSV (.csv)",
                            ExportFormat.DOCX: "Word Document (.docx)",
                            ExportFormat.PDF: "PDF (.pdf)",
                        }.get(fmt, fmt.upper())
                        
                        yield Button(format_name, id=f"format-{fmt}", variant="default", classes="format-button")
                
                # Cancel button
                yield Button("Cancel", id="cancel-button", variant="default", classes="cancel-button")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.dismiss(None)
        elif event.button.id.startswith("format-"):
            format_type = event.button.id.replace("format-", "")
            self.dismiss(format_type)


class ExportProgressScreen(ModalScreen):
    """Screen showing export progress."""
    
    def __init__(self, **kwargs):
        """Initialize the export progress screen."""
        super().__init__(**kwargs)
        
    def compose(self) -> ComposeResult:
        """Compose the export progress screen."""
        with Container(classes="export-progress-dialog"):
            with Vertical(classes="export-progress-content"):
                yield Static("[bold blue]Exporting...[/bold blue]", classes="export-header")
                yield Static("", id="progress-status", classes="progress-text")
                yield Static("Please wait while your transcription is being exported.", classes="progress-info")
                
    def update_progress(self, message: str) -> None:
        """Update the progress message."""
        try:
            status_widget = self.query_one("#progress-status", Static)
            status_widget.update(message)
        except:
            pass  # Fail silently if widget not found
            
    def on_mount(self) -> None:
        """Set up the progress screen."""
        # Auto-dismiss after a short delay if not dismissed manually
        self.set_timer(10.0, lambda: self.dismiss(None))