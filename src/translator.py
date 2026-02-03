"""Translation module using Google Translate API."""
import time
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from loguru import logger

from .subtitle_generator import TranscriptSegment
from .utils import TranslationError, APIQuotaExceeded


class Translator:
    """Translate text using Google Translate API."""

    def __init__(self, credentials_path):
        """
        Initialize translator.

        Args:
            credentials_path: Path to Google Cloud service account JSON key
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = translate.Client(credentials=credentials)
            logger.debug("Translate API client initialized")
        except Exception as e:
            raise TranslationError(
                f"Failed to initialize Translate API client: {e}"
            )

    def translate_segments(self, segments, target_language='zh-CN', batch_size=128):
        """
        Translate transcript segments from Japanese to target language.

        Args:
            segments: List of TranscriptSegment objects with Japanese text
            target_language: Target language code (default: zh-CN for Simplified Chinese)
            batch_size: Number of segments to translate per API call

        Returns:
            List[TranscriptSegment]: New segments with translated text, same timestamps

        Raises:
            TranslationError: If translation fails
        """
        if not segments:
            return []

        logger.info(f"Translating {len(segments)} segments to {target_language}...")

        translated_segments = []

        # Process in batches for efficiency
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(segments) + batch_size - 1) // batch_size

            logger.info(f"Translating batch {batch_num}/{total_batches}...")

            # Extract texts from segments
            texts = [seg.text for seg in batch]

            # Translate batch with retry logic
            translated_texts = self._translate_batch_with_retry(
                texts,
                target_language=target_language
            )

            # Create new segments with translated text but original timestamps
            for segment, translated_text in zip(batch, translated_texts):
                translated_segments.append(
                    TranscriptSegment(
                        text=translated_text,
                        start_time=segment.start_time,
                        end_time=segment.end_time,
                        confidence=segment.confidence
                    )
                )

        logger.success(f"Translation complete: {len(translated_segments)} segments")
        return translated_segments

    def _translate_batch_with_retry(self, texts, target_language, max_retries=3):
        """
        Translate a batch of texts with exponential backoff retry.

        Args:
            texts: List of text strings to translate
            target_language: Target language code
            max_retries: Maximum number of retry attempts

        Returns:
            List[str]: Translated texts

        Raises:
            TranslationError: If all retries fail
            APIQuotaExceeded: If quota is exceeded
        """
        for attempt in range(max_retries):
            try:
                # Call Google Translate API
                results = self.client.translate(
                    texts,
                    target_language=target_language,
                    source_language='ja'  # Japanese
                )

                # Extract translated text from results
                # Results can be a single dict or list of dicts
                if isinstance(results, dict):
                    return [results['translatedText']]
                else:
                    return [r['translatedText'] for r in results]

            except Exception as e:
                error_msg = str(e).lower()

                # Check for quota exceeded error
                if 'quota' in error_msg or 'limit' in error_msg:
                    raise APIQuotaExceeded(
                        f"Google Translate API quota exceeded: {e}"
                    )

                # Check if this is the last attempt
                if attempt == max_retries - 1:
                    raise TranslationError(
                        f"Translation failed after {max_retries} attempts: {e}"
                    )

                # Calculate exponential backoff delay
                delay = (2 ** attempt) * 1  # 1, 2, 4 seconds
                logger.warning(
                    f"Translation attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay} seconds..."
                )
                time.sleep(delay)

        raise TranslationError("Translation failed: max retries exceeded")
