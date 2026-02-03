"""Speech recognition module using Google Speech-to-Text API."""
from pathlib import Path
from google.cloud import speech
from google.oauth2 import service_account
from loguru import logger

from .subtitle_generator import TranscriptSegment
from .utils import TranscriptionError


class SpeechRecognizer:
    """Transcribe audio to text using Google Speech-to-Text API."""

    def __init__(self, credentials_path, language_code='ja-JP'):
        """
        Initialize speech recognizer.

        Args:
            credentials_path: Path to Google Cloud service account JSON key
            language_code: Language code for speech recognition (default: ja-JP)
        """
        self.language_code = language_code

        # Initialize Google Speech-to-Text client with credentials
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = speech.SpeechClient(credentials=credentials)
            logger.debug("Speech-to-Text client initialized")
        except Exception as e:
            raise TranscriptionError(
                f"Failed to initialize Speech-to-Text client: {e}"
            )

    def transcribe_audio(self, audio_path, sync_threshold=60):
        """
        Transcribe audio file to text with timestamps.

        Args:
            audio_path: Path to audio file (WAV format)
            sync_threshold: Use synchronous API for videos shorter than this (seconds)

        Returns:
            List[TranscriptSegment]: Transcribed segments with timestamps

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")

            # Load audio file
            with open(audio_path, 'rb') as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)

            # Configure recognition settings
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.language_code,
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
            )

            # Determine audio duration to choose API method
            from .audio_extractor import AudioExtractor
            extractor = AudioExtractor()
            duration = extractor.get_audio_duration(audio_path)

            logger.info(f"Audio duration: {duration:.2f} seconds")

            if duration < sync_threshold:
                # Use synchronous recognition for short audio
                logger.info("Using synchronous recognition (< 60 seconds)")
                response = self.client.recognize(config=config, audio=audio)
                segments = self._process_response(response)
            else:
                # Use long-running asynchronous recognition for longer audio
                logger.info("Using long-running recognition (>= 60 seconds)")
                operation = self.client.long_running_recognize(
                    config=config,
                    audio=audio
                )

                logger.info("Waiting for transcription to complete...")
                response = operation.result(timeout=7200)  # 2-hour timeout
                segments = self._process_response(response)

            logger.success(f"Transcription complete: {len(segments)} segments")
            return segments

        except TranscriptionError:
            raise
        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {e}")

    def _process_response(self, response):
        """
        Process Google Speech-to-Text API response and create segments.

        Args:
            response: API response object

        Returns:
            List[TranscriptSegment]: Processed segments with timestamps
        """
        segments = []

        for result in response.results:
            if not result.alternatives:
                continue

            alternative = result.alternatives[0]

            # If word time offsets are available, create segments from words
            if alternative.words:
                word_segments = self._create_segments_from_words(
                    alternative.words
                )
                segments.extend(word_segments)
            else:
                # Fallback: create single segment for entire result
                # Estimate timing based on result index
                start_time = len(segments) * 3.0  # Rough estimate
                end_time = start_time + 3.0
                segments.append(
                    TranscriptSegment(
                        text=alternative.transcript,
                        start_time=start_time,
                        end_time=end_time,
                        confidence=alternative.confidence
                    )
                )

        return segments

    def _create_segments_from_words(self, word_info_list, max_duration=5.0, max_chars=80):
        """
        Group words into subtitle segments with optimal timing.

        Args:
            word_info_list: List of WordInfo objects from API
            max_duration: Maximum segment duration in seconds
            max_chars: Maximum characters per segment

        Returns:
            List[TranscriptSegment]: Grouped segments
        """
        if not word_info_list:
            return []

        segments = []
        current_words = []
        current_start = None
        current_end = None

        # Japanese punctuation marks that indicate end of sentence
        sentence_endings = {'。', '！', '？', '、'}

        for word_info in word_info_list:
            # Convert Duration to float seconds
            start_sec = (
                word_info.start_time.seconds +
                word_info.start_time.microseconds / 1e6
            )
            end_sec = (
                word_info.end_time.seconds +
                word_info.end_time.microseconds / 1e6
            )

            if current_start is None:
                current_start = start_sec

            current_words.append(word_info.word)
            current_end = end_sec

            # Calculate current segment stats
            duration = current_end - current_start
            text = ''.join(current_words)

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
            text = ''.join(current_words)
            segments.append(
                TranscriptSegment(
                    text=text,
                    start_time=current_start,
                    end_time=current_end,
                    confidence=1.0
                )
            )

        return segments
