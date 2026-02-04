"""
Chinese Subtitle Generator for Japanese Movies

A CLI tool to generate Chinese subtitles from Japanese language videos.
"""
import sys
from pathlib import Path
import click
from loguru import logger

from config.settings import Settings
from src.audio_extractor import AudioExtractor
from src.speech_recognizer import SpeechRecognizer
from src.translator import Translator
from src.subtitle_generator import SubtitleGenerator
from src.utils import (
    setup_logging,
    validate_video_file,
    cleanup_temp_files,
    format_duration,
    VideoFileError,
    SubtitleGeneratorError
)


@click.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option(
    '-o', '--output',
    'output_path',
    type=click.Path(),
    help='Output SRT file path (default: <video_name>.srt)'
)
@click.option(
    '-c', '--credentials',
    'credentials_path',
    type=click.Path(exists=True),
    help='Google Cloud credentials JSON file'
)
@click.option(
    '--keep-temp',
    is_flag=True,
    help='Keep temporary audio files after processing'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enable verbose logging (DEBUG level)'
)
@click.option(
    '--target-lang',
    default='zh-CN',
    type=click.Choice(['zh-CN', 'zh-TW']),
    help='Target Chinese variant: zh-CN (Simplified) or zh-TW (Traditional)'
)
def main(video_path, output_path, credentials_path, keep_temp, verbose, target_lang):
    """
    Generate Chinese subtitles for Japanese language movies.

    \b
    Example usage:
        python main.py movie.mp4
        python main.py movie.mp4 -o subtitles.srt
        python main.py movie.mp4 --target-lang zh-TW --verbose
    """
    # Setup logging
    setup_logging(verbose)

    logger.info("=" * 60)
    logger.info("Chinese Subtitle Generator for Japanese Movies")
    logger.info("=" * 60)

    try:
        # Initialize settings
        settings = Settings(credentials_path)
        settings.validate()

        # Update target language in settings
        settings.translation_config['target_language'] = target_lang

        # Generate default output path if not provided
        if not output_path:
            output_path = Path(video_path).stem + '.srt'

        logger.info(f"Input video: {video_path}")
        logger.info(f"Output subtitle: {output_path}")
        logger.info(f"Target language: {target_lang}")
        logger.info("-" * 60)

        # Step 1: Validate input video
        logger.info("Step 1/5: Validating video file...")
        validate_video_file(video_path)
        logger.success("Video file validated")

        # Step 2: Extract audio from video
        logger.info("Step 2/5: Extracting audio from video...")
        extractor = AudioExtractor(
            sample_rate=settings.audio_config['sample_rate'],
            channels=settings.audio_config['channels']
        )
        audio_path = extractor.extract_audio(video_path, settings.temp_dir)
        duration = extractor.get_audio_duration(audio_path)
        logger.success(f"Audio extracted: {format_duration(duration)}")

        # Step 3: Transcribe Japanese audio
        logger.info("Step 3/5: Transcribing Japanese audio to text...")
        recognizer = SpeechRecognizer(
            credentials_path=settings.credentials_path,
            language_code=settings.speech_config['language_code'],
            gcs_bucket_name=settings.gcs_bucket_name
        )
        japanese_segments = recognizer.transcribe_audio(
            audio_path,
            sync_threshold=settings.speech_config['sync_threshold_seconds']
        )
        logger.success(f"Transcription complete: {len(japanese_segments)} segments")

        # Step 4: Translate to Chinese
        logger.info("Step 4/5: Translating Japanese to Chinese...")
        translator = Translator(credentials_path=settings.credentials_path)
        chinese_segments = translator.translate_segments(
            japanese_segments,
            target_language=target_lang,
            batch_size=settings.translation_config['batch_size']
        )
        logger.success(f"Translation complete: {len(chinese_segments)} segments")

        # Step 5: Generate SRT subtitle file
        logger.info("Step 5/5: Generating SRT subtitle file...")
        generator = SubtitleGenerator(
            min_duration=settings.subtitle_config['min_segment_duration'],
            max_chars=settings.subtitle_config['max_chars_per_segment']
        )
        output_file = generator.generate_srt(chinese_segments, output_path)
        logger.success(f"Subtitle file created: {output_file}")

        # Cleanup temporary files
        if not keep_temp:
            logger.info("Cleaning up temporary files...")
            cleanup_temp_files(settings.temp_dir)

        # Success summary
        logger.info("=" * 60)
        logger.success("SUBTITLE GENERATION COMPLETE!")
        logger.info(f"Video duration: {format_duration(duration)}")
        logger.info(f"Subtitle segments: {len(chinese_segments)}")
        logger.info(f"Output file: {output_file}")
        logger.info("=" * 60)

        return 0

    except VideoFileError as e:
        logger.error(f"Video file error: {e}")
        return 1
    except SubtitleGeneratorError as e:
        logger.error(f"Subtitle generation error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
