"""
Unit tests for the ExportManager class.

This module contains comprehensive tests for the export functionality
including format support, filtering, and error handling.
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from src.cli_whisperer.utils.export_manager import ExportFormat, ExportManager, ExportOptions


class TestExportManager(unittest.TestCase):
    """Test cases for the ExportManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.export_manager = ExportManager()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Sample transcription data
        self.sample_text = "This is a test transcription."
        self.sample_formatted_text = "# Test Transcription\n\nThis is a **test** transcription."
        self.sample_timestamp = "2025-01-01T12:00:00"
        self.sample_metadata = {"model": "base", "duration": 5.0}
        
        # Sample history data
        self.sample_history = [
            {
                "timestamp": "2025-01-01T12:00:00",
                "text": "First transcription",
                "formatted_text": "# First Transcription\n\nFirst transcription",
                "model": "base",
                "working_dir": "/home/user"
            },
            {
                "timestamp": "2025-01-01T12:05:00",
                "text": "Second transcription",
                "formatted_text": None,
                "model": "base",
                "working_dir": "/home/user"
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_supported_formats(self):
        """Test getting supported export formats."""
        formats = self.export_manager.get_supported_formats()
        
        # Basic formats should always be available
        self.assertIn(ExportFormat.TXT, formats)
        self.assertIn(ExportFormat.MD, formats)
        self.assertIn(ExportFormat.JSON, formats)
        self.assertIn(ExportFormat.CSV, formats)
        
        # Optional formats depend on library availability
        self.assertIsInstance(formats, list)
        self.assertTrue(len(formats) >= 4)
    
    def test_export_single_transcription_txt(self):
        """Test exporting a single transcription as TXT."""
        output_path = self.temp_path / "test.txt"
        
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            formatted_text=self.sample_formatted_text,
            timestamp=self.sample_timestamp,
            output_path=output_path,
            format_type=ExportFormat.TXT
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(self.sample_text, content)
            self.assertIn(self.sample_formatted_text, content)
            self.assertIn(self.sample_timestamp, content)
    
    def test_export_single_transcription_md(self):
        """Test exporting a single transcription as Markdown."""
        output_path = self.temp_path / "test.md"
        
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            formatted_text=self.sample_formatted_text,
            timestamp=self.sample_timestamp,
            output_path=output_path,
            format_type=ExportFormat.MD
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# Transcription", content)
            self.assertIn("## Raw Transcription", content)
            self.assertIn("## AI-Formatted Transcription", content)
    
    def test_export_single_transcription_json(self):
        """Test exporting a single transcription as JSON."""
        output_path = self.temp_path / "test.json"
        
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            formatted_text=self.sample_formatted_text,
            timestamp=self.sample_timestamp,
            metadata=self.sample_metadata,
            output_path=output_path,
            format_type=ExportFormat.JSON
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['raw_text'], self.sample_text)
            self.assertEqual(data['formatted_text'], self.sample_formatted_text)
            self.assertEqual(data['timestamp'], self.sample_timestamp)
            self.assertEqual(data['metadata'], self.sample_metadata)
    
    def test_export_single_transcription_csv(self):
        """Test exporting a single transcription as CSV."""
        output_path = self.temp_path / "test.csv"
        
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            formatted_text=self.sample_formatted_text,
            timestamp=self.sample_timestamp,
            output_path=output_path,
            format_type=ExportFormat.CSV
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("timestamp", content)
            self.assertIn("raw_text", content)
            self.assertIn("formatted_text", content)
            self.assertIn(self.sample_text, content)
    
    def test_export_history_json(self):
        """Test exporting history data as JSON."""
        output_path = self.temp_path / "history.json"
        
        result_path = self.export_manager.export_history(
            history_data=self.sample_history,
            output_path=output_path,
            format_type=ExportFormat.JSON
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('export_timestamp', data)
            self.assertIn('entries', data)
            self.assertEqual(len(data['entries']), 2)
    
    def test_export_history_csv(self):
        """Test exporting history data as CSV."""
        output_path = self.temp_path / "history.csv"
        
        result_path = self.export_manager.export_history(
            history_data=self.sample_history,
            output_path=output_path,
            format_type=ExportFormat.CSV
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("timestamp", content)
            self.assertIn("First transcription", content)
            self.assertIn("Second transcription", content)
    
    def test_export_options_filtering(self):
        """Test export options for filtering content."""
        options = ExportOptions(
            include_raw_text=True,
            include_formatted_text=False,
            include_timestamps=False,
            include_metadata=False
        )
        
        output_path = self.temp_path / "filtered.json"
        
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            formatted_text=self.sample_formatted_text,
            timestamp=self.sample_timestamp,
            metadata=self.sample_metadata,
            output_path=output_path,
            format_type=ExportFormat.JSON,
            options=options
        )
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('raw_text', data)
            self.assertNotIn('formatted_text', data)
            self.assertNotIn('timestamp', data)
            self.assertNotIn('metadata', data)
    
    def test_apply_filters_date_range(self):
        """Test filtering by date range."""
        filter_criteria = {
            'date_from': datetime(2025, 1, 1, 12, 0, 0),
            'date_to': datetime(2025, 1, 1, 12, 3, 0)
        }
        
        filtered_data = self.export_manager._apply_filters(
            self.sample_history, filter_criteria
        )
        
        # Should only include the first entry
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]['text'], "First transcription")
    
    def test_apply_filters_working_directory(self):
        """Test filtering by working directory."""
        filter_criteria = {
            'working_dir': '/home/user'
        }
        
        filtered_data = self.export_manager._apply_filters(
            self.sample_history, filter_criteria
        )
        
        # Should include both entries
        self.assertEqual(len(filtered_data), 2)
    
    def test_apply_filters_text_search(self):
        """Test filtering by text search."""
        filter_criteria = {
            'text_search': 'First'
        }
        
        filtered_data = self.export_manager._apply_filters(
            self.sample_history, filter_criteria
        )
        
        # Should only include the first entry
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]['text'], "First transcription")
    
    def test_default_filename_generation(self):
        """Test that default filenames are generated correctly."""
        result_path = self.export_manager.export_single_transcription(
            text=self.sample_text,
            format_type=ExportFormat.TXT
        )
        
        # Should create a file with timestamp
        self.assertTrue(result_path.exists())
        self.assertTrue(result_path.name.startswith("transcription_"))
        self.assertTrue(result_path.name.endswith(".txt"))
        
        # Clean up
        result_path.unlink()
    
    def test_unsupported_format_error(self):
        """Test that unsupported formats raise an error."""
        with self.assertRaises(ValueError):
            self.export_manager.export_single_transcription(
                text=self.sample_text,
                format_type="unsupported_format"
            )
    
    def test_export_session_data(self):
        """Test exporting session data."""
        session_entries = [
            Mock(text="Entry 1", formatted_text="# Entry 1", timestamp="12:00:00", entry_id="1"),
            Mock(text="Entry 2", formatted_text=None, timestamp="12:05:00", entry_id="2")
        ]
        
        output_path = self.temp_path / "session.json"
        
        result_path = self.export_manager.export_session_data(
            session_entries=session_entries,
            output_path=output_path,
            format_type=ExportFormat.JSON
        )
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(output_path.exists())
        
        # Check content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('entries', data)
            self.assertEqual(len(data['entries']), 2)
    
    @patch('src.cli_whisperer.utils.export_manager.DOCX_AVAILABLE', True)
    def test_docx_export_when_available(self):
        """Test DOCX export when python-docx is available."""
        formats = self.export_manager.get_supported_formats()
        self.assertIn(ExportFormat.DOCX, formats)
    
    @patch('src.cli_whisperer.utils.export_manager.PDF_AVAILABLE', True)
    def test_pdf_export_when_available(self):
        """Test PDF export when reportlab is available."""
        formats = self.export_manager.get_supported_formats()
        self.assertIn(ExportFormat.PDF, formats)
    
    def test_export_with_transcript_manager(self):
        """Test export with transcript manager integration."""
        mock_transcript_manager = Mock()
        mock_transcript_manager.base_dir = self.temp_path
        
        export_manager = ExportManager(transcript_manager=mock_transcript_manager)
        
        result_path = export_manager.export_single_transcription(
            text=self.sample_text,
            format_type=ExportFormat.TXT
        )
        
        self.assertTrue(result_path.exists())
        self.assertTrue(result_path.name.startswith("transcription_"))
    
    def test_export_with_history_manager(self):
        """Test export with history manager integration."""
        mock_history_manager = Mock()
        mock_history_manager.get_history.return_value = self.sample_history
        
        export_manager = ExportManager(history_manager=mock_history_manager)
        
        # This would be called by the actual UI code
        history_data = mock_history_manager.get_history()
        
        result_path = export_manager.export_history(
            history_data=history_data,
            output_path=self.temp_path / "history.json",
            format_type=ExportFormat.JSON
        )
        
        self.assertTrue(result_path.exists())
        mock_history_manager.get_history.assert_called_once()


class TestExportOptions(unittest.TestCase):
    """Test cases for the ExportOptions class."""
    
    def test_default_options(self):
        """Test default export options."""
        options = ExportOptions()
        
        self.assertTrue(options.include_metadata)
        self.assertTrue(options.include_timestamps)
        self.assertTrue(options.include_raw_text)
        self.assertTrue(options.include_formatted_text)
        self.assertFalse(options.include_file_paths)
        self.assertFalse(options.include_working_dir)
        self.assertEqual(options.date_format, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(options.encoding, "utf-8")
    
    def test_custom_options(self):
        """Test custom export options."""
        options = ExportOptions(
            include_metadata=False,
            include_timestamps=False,
            include_raw_text=False,
            include_formatted_text=True,
            include_file_paths=True,
            include_working_dir=True,
            date_format="%Y-%m-%d",
            encoding="latin-1"
        )
        
        self.assertFalse(options.include_metadata)
        self.assertFalse(options.include_timestamps)
        self.assertFalse(options.include_raw_text)
        self.assertTrue(options.include_formatted_text)
        self.assertTrue(options.include_file_paths)
        self.assertTrue(options.include_working_dir)
        self.assertEqual(options.date_format, "%Y-%m-%d")
        self.assertEqual(options.encoding, "latin-1")


if __name__ == '__main__':
    unittest.main()