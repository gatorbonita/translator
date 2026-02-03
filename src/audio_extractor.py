"""Audio extraction module using MoviePy."""
import os
from pathlib import Path
from datetime import datetime
from moviepy.editor import VideoFileClip
from loguru import logger

from .utils import AudioExtractionError


class AudioExtractor:
    """Extract audio from video files using MoviePy."""

    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize audio extractor.

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000 for speech)
            channels: Number of audio channels (1=mono, 2=stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def extract_audio(self, video_path, temp_dir='./temp'):
        """
        Extract audio from video and save as WAV file.

        Args:
            video_path: Path to input video file
            temp_dir: Directory to save temporary audio file

        Returns:
            str: Path to extracted audio file

        Raises:
            AudioExtractionError: If extraction fails
        """
        try:
            video_path = Path(video_path)
            temp_dir = Path(temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique temp filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"audio_{timestamp}.wav"
            audio_path = temp_dir / audio_filename

            logger.info(f"Loading video: {video_path}")
            video = VideoFileClip(str(video_path))

            if video.audio is None:
                raise AudioExtractionError(
                    f"Video has no audio track: {video_path}"
                )

            logger.info(
                f"Extracting audio (sample_rate={self.sample_rate}Hz, "
                f"channels={self.channels})..."
            )

            # Extract audio and save as WAV
            audio = video.audio
            audio.write_audiofile(
                str(audio_path),
                fps=self.sample_rate,  # Sample rate
                nbytes=2,  # 16-bit audio (2 bytes per sample)
                codec='pcm_s16le',  # LINEAR16 encoding
                ffmpeg_params=['-ac', str(self.channels)],  # Set channels
                logger=None,  # Disable MoviePy's default logging
                verbose=False
            )

            # Close video to free resources
            video.close()

            logger.success(f"Audio extracted: {audio_path}")
            return str(audio_path)

        except AudioExtractionError:
            raise
        except Exception as e:
            raise AudioExtractionError(
                f"Failed to extract audio from {video_path}: {e}"
            )

    def get_audio_duration(self, audio_path):
        """
        Get duration of audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            float: Duration in seconds

        Raises:
            AudioExtractionError: If unable to read audio file
        """
        try:
            from moviepy.editor import AudioFileClip

            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()

            return duration

        except Exception as e:
            raise AudioExtractionError(
                f"Failed to get audio duration from {audio_path}: {e}"
            )
