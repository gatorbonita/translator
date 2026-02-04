"""Subtitle generation module for creating SRT files."""
from pathlib import Path
from dataclasses import dataclass
from typing import List
from loguru import logger


@dataclass
class TranscriptSegment:
    """Represents a subtitle segment with text and timing information."""
    text: str
    start_time: float  # seconds from start
    end_time: float  # seconds from start
    confidence: float = 1.0


class SubtitleGenerator:
    """Generate SRT subtitle files from transcript segments."""

    def __init__(self, min_duration=1.0, max_chars=80):
        """
        Initialize subtitle generator.

        Args:
            min_duration: Minimum subtitle duration in seconds
            max_chars: Maximum characters per subtitle line
        """
        self.min_duration = min_duration
        self.max_chars = max_chars

    def generate_srt(self, segments, output_path):
        """
        Generate SRT subtitle file from transcript segments.

        Args:
            segments: List of TranscriptSegment objects
            output_path: Path to output SRT file

        Returns:
            str: Path to generated SRT file
        """
        logger.info(f"Generating SRT file with {len(segments)} segments...")

        # Merge short segments for better readability
        merged_segments = self._merge_short_segments(segments)

        # Write SRT file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(merged_segments, start=1):
                # Subtitle index
                f.write(f"{i}\n")

                # Timestamp range
                start_ts = self._format_timestamp(segment.start_time)
                end_ts = self._format_timestamp(segment.end_time)
                f.write(f"{start_ts} --> {end_ts}\n")

                # Subtitle text
                f.write(f"{segment.text}\n")

                # Blank line separator
                f.write("\n")

        logger.success(f"SRT file generated: {output_path}")
        return str(output_path)

    def _format_timestamp(self, seconds):
        """
        Convert seconds to SRT timestamp format: HH:MM:SS,mmm

        Args:
            seconds: Time in seconds

        Returns:
            str: Formatted timestamp (e.g., "00:01:05,500")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def _merge_short_segments(self, segments):
        """
        Merge segments that are too short for readability.

        Args:
            segments: List of TranscriptSegment objects

        Returns:
            List[TranscriptSegment]: Merged segments
        """
        if not segments:
            return []

        merged = []
        current = None

        for segment in segments:
            if current is None:
                current = TranscriptSegment(
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence
                )
                continue

            duration = current.end_time - current.start_time
            combined_text = current.text + " " + segment.text

            # Check if we should merge with current segment
            should_merge = (
                duration < self.min_duration or  # Current too short
                (
                    len(combined_text) <= self.max_chars and  # Won't exceed max chars
                    segment.start_time - current.end_time < 1.0  # Close timing
                )
            )

            if should_merge:
                # Merge with current segment
                current.text = combined_text
                current.end_time = segment.end_time
            else:
                # Finalize current segment and start new one
                merged.append(current)
                current = TranscriptSegment(
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence
                )

        # Add the last segment
        if current is not None:
            merged.append(current)

        logger.debug(f"Merged {len(segments)} segments into {len(merged)} segments")
        return merged
