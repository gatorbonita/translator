"""Utility functions and custom exceptions."""
import os
import sys
from pathlib import Path
from loguru import logger


# Custom Exceptions
class SubtitleGeneratorError(Exception):
    """Base exception for subtitle generator."""
    pass


class VideoFileError(SubtitleGeneratorError):
    """Invalid or corrupt video file."""
    pass


class AudioExtractionError(SubtitleGeneratorError):
    """Failed to extract audio from video."""
    pass


class TranscriptionError(SubtitleGeneratorError):
    """Speech recognition failed."""
    pass


class TranslationError(SubtitleGeneratorError):
    """Translation API failed."""
    pass


class APIQuotaExceeded(SubtitleGeneratorError):
    """Google Cloud API quota exceeded."""
    pass


# Utility Functions
def setup_logging(verbose=False):
    """Configure logging with loguru."""
    # Remove default handler
    logger.remove()

    # Add console handler with appropriate level
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Add file handler for all logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "subtitle_generator.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )


def validate_video_file(path):
    """
    Validate that the video file exists and has a valid extension.

    Args:
        path: Path to video file

    Returns:
        bool: True if valid

    Raises:
        VideoFileError: If file is invalid
    """
    path = Path(path)

    if not path.exists():
        raise VideoFileError(f"Video file not found: {path}")

    if not path.is_file():
        raise VideoFileError(f"Path is not a file: {path}")

    # Common video extensions
    valid_extensions = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'
    }

    if path.suffix.lower() not in valid_extensions:
        raise VideoFileError(
            f"Unsupported video format: {path.suffix}. "
            f"Supported formats: {', '.join(valid_extensions)}"
        )

    return True


def cleanup_temp_files(temp_dir):
    """
    Remove temporary audio files from the temp directory.

    Args:
        temp_dir: Path to temporary directory
    """
    temp_dir = Path(temp_dir)
    if not temp_dir.exists():
        return

    # Remove all .wav files in temp directory
    for audio_file in temp_dir.glob("*.wav"):
        try:
            audio_file.unlink()
            logger.debug(f"Removed temporary file: {audio_file}")
        except Exception as e:
            logger.warning(f"Failed to remove {audio_file}: {e}")


def format_duration(seconds):
    """
    Format seconds to human-readable duration string.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., "2h 35m 10s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)
