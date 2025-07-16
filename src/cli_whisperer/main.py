"""
Main entry point for the CLI Whisperer application.

This module handles command-line argument parsing and application initialization.
"""

import argparse
import sys

# Version info
__version__ = "1.0.0"
from .cli import CLIApplication
from .utils.config import (
    DEFAULT_CLEANUP_DAYS,
    DEFAULT_MAX_RECENT_FILES,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_RECORDING_DURATION,
    DEFAULT_WHISPER_MODEL,
    LONG_RECORDING_WARNING_SECONDS
)


def check_dependencies(no_openai: bool = False) -> None:
    """
    Check if all required dependencies are installed.

    Args:
        no_openai (bool): Whether OpenAI is disabled.

    Raises:
        SystemExit: If required packages are missing.
    """
    required = ['transformers', 'torch', 'sounddevice', 'scipy', 'pyperclip', 'numpy']
    if not no_openai:
        required.append('openai')
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Voice to Text Tool with Smart File Management")
    parser.add_argument("--version", action="version", version=f"CLI Whisperer {__version__}")
    parser.add_argument("-m", "--model", default=DEFAULT_WHISPER_MODEL, type=str,
                       choices=["tiny", "base", "turbo", "small", "medium", "large"],
                       help=f"Whisper model to use (default: {DEFAULT_WHISPER_MODEL})")
    parser.add_argument("-d", "--duration", type=int, default=DEFAULT_RECORDING_DURATION,
                       help=f"Recording duration in seconds (default: {DEFAULT_RECORDING_DURATION})")
    parser.add_argument("-min", "--minutes", type=float,
                       help="Recording duration in minutes (overrides -d if set)")
    # Modern CLI arguments (primary)
    parser.add_argument("--tui", action="store_true", default=False,
                       help="Launch interactive TUI mode")
    parser.add_argument("--once", action="store_true", default=False,
                       help="Record once and exit")
    parser.add_argument("--format", action="store_true", default=False,
                       help="Enable OpenAI text formatting")
    parser.add_argument("--no-format", action="store_true", default=False,
                       help="Disable OpenAI text formatting (raw transcription only)")
    parser.add_argument("--theme", type=str, default="marc_anthony",
                       choices=["edm_synthwave", "edm_cyberpunk", "edm_trance", "marc_anthony", 
                               "professional", "dark_minimal", "neon_noir", "retro_wave"],
                       help="TUI theme selection (default: marc_anthony)")
    parser.add_argument("--debug", action="store_true", default=False,
                       help="Enable debug logging")
    parser.add_argument("--openai-model", type=str, default=DEFAULT_OPENAI_MODEL,
                       help=f"OpenAI model for formatting (default: {DEFAULT_OPENAI_MODEL})")
    
    # Backward compatibility aliases
    parser.add_argument("-s", "--single-run", action="store_true", default=False,
                       help="Run once, defaults to running continuously (alias for --once)")
    parser.add_argument("--no-openai", action="store_true",
                       help="Disable OpenAI formatting (alias for --no-format)")
    parser.add_argument("--ai-model", type=str, default=DEFAULT_OPENAI_MODEL,
                       help=f"OpenAI model to use for formatting (alias for --openai-model)")
    
    # Additional arguments
    parser.add_argument("--history", type=int, metavar="N",
                       help="Show last N transcriptions and exit")
    parser.add_argument("--openai-key", type=str,
                       help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--max-recent", type=int, default=DEFAULT_MAX_RECENT_FILES,
                       help=f"Number of recent files to keep (default: {DEFAULT_MAX_RECENT_FILES})")
    parser.add_argument("--cleanup-days", type=int, default=DEFAULT_CLEANUP_DAYS,
                       help=f"Delete old files after this many days (default: {DEFAULT_CLEANUP_DAYS})")
    parser.add_argument("--device", type=int,
                       help="Audio input device number (use -1 to list devices)")
    parser.add_argument("--no-spotify", action="store_true",
                       help="Disable automatic Spotify pause/resume during recording")
    parser.add_argument("--output-dir", type=str,
                       help="Directory to save transcripts (default: current directory/transcripts)")
    
    return parser


def process_arguments(args: argparse.Namespace) -> int:
    """
    Process command-line arguments and calculate recording duration.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Recording duration in seconds.
    """
    # Convert minutes to seconds if specified
    duration = args.duration
    if args.minutes:
        duration = int(args.minutes * 60)
        print(f"📢 Recording duration set to {args.minutes} minutes ({duration} seconds)")
    
    # Warn if duration is very long
    if duration > LONG_RECORDING_WARNING_SECONDS:
        print(f"⚠️  Warning: Long recording duration ({duration} seconds / {duration/60:.1f} minutes)")
        print("   This may take a while to process. Consider using shorter durations.")
    
    return duration


def main() -> None:
    """Main entry point for the CLI Whisperer application."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Calculate recording duration
    duration = process_arguments(args)
    
    # Handle modern CLI arguments - resolve aliases and conflicts
    # Format handling: --format vs --no-format vs --no-openai
    format_enabled = args.format
    no_openai = args.no_openai or args.no_format
    if args.no_format and args.format:
        print("❌ Error: Cannot use both --format and --no-format")
        sys.exit(1)
    
    # Single run: --once vs --single-run
    single_run = args.once or args.single_run
    
    # OpenAI model: --openai-model vs --ai-model
    openai_model = args.openai_model or args.ai_model
    
    # Check dependencies
    check_dependencies(no_openai)
    
    # TUI mode - force TUI by setting environment variable
    if args.tui:
        import os
        os.environ['CLI_WHISPERER_TUI'] = '1'
        if args.debug:
            os.environ['CLI_WHISPERER_DEBUG'] = '1'
        if args.theme:
            os.environ['CLI_WHISPERER_THEME'] = args.theme
    
    # Create CLI application instance
    app = CLIApplication(
        model_name=args.model,
        no_openai=no_openai,
        openai_model=openai_model,
        openai_api_key=args.openai_key,
        input_device=args.device,
        no_spotify_control=args.no_spotify,
        max_recent=args.max_recent,
        cleanup_days=args.cleanup_days,
        single_run=single_run,
        output_dir=args.output_dir
    )
    
    # Show history and exit if requested
    if args.history:
        app.show_history(args.history)
        return
    
    # Run in appropriate mode
    if single_run and not args.tui:
        app.record_once(duration=duration)
    else:
        app.continuous_mode(duration=duration)


if __name__ == "__main__":
    main()