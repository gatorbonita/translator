"""Speech recognition module using Whisper (faster-whisper)."""
from pathlib import Path
from faster_whisper import WhisperModel
from loguru import logger

from .subtitle_generator import TranscriptSegment
from .utils import TranscriptionError


class SpeechRecognizer:
    """Transcribe audio to text using Whisper (OpenAI's speech recognition model)."""

    def __init__(self, model_size='medium', device='auto', language='ja'):
        """
        Initialize Whisper speech recognizer.

        Args:
            model_size: Whisper model size - 'tiny', 'base', 'small', 'medium', 'large-v3'
                       Recommended for Japanese: 'medium' (good balance) or 'large-v3' (best quality)
            device: Device to run on - 'auto', 'cpu', 'cuda' (auto detects GPU if available)
            language: Language code for transcription (default: 'ja' for Japanese)
        """
        self.model_size = model_size
        self.language = language

        try:
            logger.info(f"Loading Whisper model: {model_size}")
            logger.info("This may take a few minutes on first run (downloading model)...")

            # Determine compute type based on device
            if device == 'auto':
                # Try CUDA first, fall back to CPU
                try:
                    import torch
                    if torch.cuda.is_available():
                        device = 'cuda'
                        compute_type = 'float16'
                        logger.info("GPU detected! Using CUDA for faster processing")
                    else:
                        device = 'cpu'
                        compute_type = 'int8'
                        logger.info("No GPU detected, using CPU")
                except ImportError:
                    device = 'cpu'
                    compute_type = 'int8'
                    logger.info("PyTorch not found, using CPU")
            elif device == 'cuda':
                compute_type = 'float16'
            else:
                compute_type = 'int8'

            # Initialize Whisper model
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root=None  # Uses default cache directory
            )

            logger.success(
                f"Whisper model loaded: {model_size} on {device} "
                f"(compute_type: {compute_type})"
            )

        except Exception as e:
            raise TranscriptionError(
                f"Failed to initialize Whisper model '{model_size}': {e}"
            )

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file to text with timestamps using Whisper.

        Args:
            audio_path: Path to audio file (WAV format recommended)

        Returns:
            List[TranscriptSegment]: Transcribed segments with timestamps

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio with Whisper: {audio_path}")

            # Transcribe with Whisper
            # word_timestamps=True gives us word-level timing for better subtitle sync
            segments, info = self.model.transcribe(
                audio_path,
                language=self.language,
                beam_size=5,  # Higher beam size = better quality, slower
                word_timestamps=True,  # Enable word-level timestamps
                vad_filter=True,  # Voice Activity Detection to remove silence
                vad_parameters=dict(
                    min_silence_duration_ms=500  # Minimum silence duration
                )
            )

            logger.info(
                f"Detected language: {info.language} "
                f"(probability: {info.language_probability:.2%})"
            )

            # Process segments into our format
            transcript_segments = []

            for segment in segments:
                # Create segment with word-level detail if available
                if segment.words:
                    # Group words into subtitle-friendly segments
                    word_segments = self._create_segments_from_words(segment.words)
                    transcript_segments.extend(word_segments)
                else:
                    # Fall back to segment-level timing
                    transcript_segments.append(
                        TranscriptSegment(
                            text=segment.text.strip(),
                            start_time=segment.start,
                            end_time=segment.end,
                            confidence=1.0  # Whisper doesn't provide confidence scores
                        )
                    )

            logger.success(
                f"Transcription complete: {len(transcript_segments)} segments "
                f"({sum(1 for s in segments if s.words)} with word timing)"
            )

            return transcript_segments

        except TranscriptionError:
            raise
        except Exception as e:
            raise TranscriptionError(f"Whisper transcription failed: {e}")

    def _create_segments_from_words(self, words, max_duration=5.0, max_chars=80):
        """
        Group words into subtitle segments with optimal timing.

        Args:
            words: List of Word objects from Whisper
            max_duration: Maximum segment duration in seconds
            max_chars: Maximum characters per segment

        Returns:
            List[TranscriptSegment]: Grouped segments
        """
        if not words:
            return []

        segments = []
        current_words = []
        current_start = None
        current_end = None

        # Japanese punctuation marks that indicate end of sentence
        sentence_endings = {'。', '！', '？', '、'}

        for word in words:
            if current_start is None:
                current_start = word.start

            current_words.append(word.word)
            current_end = word.end

            # Calculate current segment stats
            duration = current_end - current_start
            text = ''.join(current_words).strip()

            # Determine if we should finalize this segment
            should_finalize = False

            # Check various conditions for segment finalization
            if duration >= max_duration:
                should_finalize = True
            elif len(text) >= max_chars:
                should_finalize = True
            elif any(text.endswith(punct) for punct in sentence_endings):
                # End on sentence punctuation if we have reasonable length
                if len(text) > 10 or duration > 1.0:
                    should_finalize = True

            if should_finalize:
                # Create segment
                segments.append(
                    TranscriptSegment(
                        text=text,
                        start_time=current_start,
                        end_time=current_end,
                        confidence=1.0
                    )
                )

                # Reset for next segment
                current_words = []
                current_start = None
                current_end = None

        # Handle remaining words
        if current_words:
            text = ''.join(current_words).strip()
            if text:  # Only add if not empty
                segments.append(
                    TranscriptSegment(
                        text=text,
                        start_time=current_start,
                        end_time=current_end,
                        confidence=1.0
                    )
                )

        return segments
