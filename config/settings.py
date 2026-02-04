"""Configuration settings for subtitle generator."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""

    def __init__(self, credentials_path=None):
        """Initialize settings with optional credentials path override."""
        # Google Cloud credentials
        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_APPLICATION_CREDENTIALS'
        )

        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

        # Temporary directory for audio files
        self.temp_dir = Path(os.getenv('TEMP_DIR', './temp'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Audio processing settings
        self.audio_config = {
            'sample_rate': 16000,  # Hz, optimal for speech recognition
            'channels': 1,  # Mono
            'format': 'wav',
            'encoding': 'LINEAR16'
        }

        # Speech recognition settings
        self.speech_config = {
            'language_code': 'ja-JP',  # Japanese
            'enable_word_time_offsets': True,
            'enable_automatic_punctuation': True,
            'sync_threshold_seconds': 60,  # Use sync API for videos < 60s
            'chunk_duration_seconds': 300  # 5-minute chunks for very long videos
        }

        # Google Cloud Storage settings (for large audio files > 10MB)
        self.gcs_bucket_name = os.getenv('GCS_BUCKET_NAME', None)

        # Translation settings
        self.translation_config = {
            'source_language': 'ja',  # Japanese
            'target_language': 'zh-CN',  # Simplified Chinese (default)
            'batch_size': 128  # Max segments per API call
        }

        # Subtitle generation settings
        self.subtitle_config = {
            'min_segment_duration': 1.0,  # Minimum subtitle duration in seconds
            'max_segment_duration': 5.0,  # Maximum subtitle duration in seconds
            'max_chars_per_segment': 80,  # Maximum characters per subtitle line
            'min_gap_between_subtitles': 0.2  # Minimum gap in seconds
        }

    def validate(self):
        """Validate that required settings are configured."""
        if not self.credentials_path:
            raise ValueError(
                "Google Cloud credentials not configured. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable "
                "or provide credentials_path parameter."
            )

        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}"
            )

        return True
