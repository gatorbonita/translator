"""Tests for subtitle generator module."""
import pytest
from pathlib import Path
import tempfile

from src.subtitle_generator import SubtitleGenerator, TranscriptSegment


class TestSubtitleGenerator:
    """Test cases for SubtitleGenerator class."""

    def test_format_timestamp_zero(self):
        """Test timestamp formatting for zero seconds."""
        generator = SubtitleGenerator()
        assert generator._format_timestamp(0) == "00:00:00,000"

    def test_format_timestamp_subsecond(self):
        """Test timestamp formatting for subsecond values."""
        generator = SubtitleGenerator()
        assert generator._format_timestamp(0.5) == "00:00:00,500"
        assert generator._format_timestamp(0.123) == "00:00:00,123"
        assert generator._format_timestamp(0.999) == "00:00:00,999"

    def test_format_timestamp_seconds(self):
        """Test timestamp formatting for seconds."""
        generator = SubtitleGenerator()
        assert generator._format_timestamp(30) == "00:00:30,000"
        assert generator._format_timestamp(45.5) == "00:00:45,500"

    def test_format_timestamp_minutes(self):
        """Test timestamp formatting for minutes."""
        generator = SubtitleGenerator()
        assert generator._format_timestamp(60) == "00:01:00,000"
        assert generator._format_timestamp(65.123) == "00:01:05,123"
        assert generator._format_timestamp(90.5) == "00:01:30,500"

    def test_format_timestamp_hours(self):
        """Test timestamp formatting for hours."""
        generator = SubtitleGenerator()
        assert generator._format_timestamp(3600) == "01:00:00,000"
        assert generator._format_timestamp(3661.5) == "01:01:01,500"
        assert generator._format_timestamp(7322.25) == "02:02:02,250"

    def test_merge_short_segments(self):
        """Test merging of short segments."""
        generator = SubtitleGenerator(min_duration=2.0)

        segments = [
            TranscriptSegment("短い", 0.0, 0.5, 1.0),
            TranscriptSegment("文章", 0.6, 1.0, 1.0),
            TranscriptSegment("これは長い文章です", 1.5, 4.0, 1.0),
        ]

        merged = generator._merge_short_segments(segments)

        # First two short segments should be merged
        assert len(merged) == 2
        assert merged[0].text == "短い 文章"
        assert merged[0].start_time == 0.0
        assert merged[0].end_time == 1.0

    def test_merge_respects_max_chars(self):
        """Test that merging respects max character limit."""
        generator = SubtitleGenerator(max_chars=20)

        segments = [
            TranscriptSegment("これは短い文章", 0.0, 1.0, 1.0),
            TranscriptSegment("これは別の短い文章", 1.1, 2.0, 1.0),
            TranscriptSegment("三番目", 2.1, 3.0, 1.0),
        ]

        merged = generator._merge_short_segments(segments)

        # Should not merge if it would exceed max_chars
        for segment in merged:
            assert len(segment.text) <= 20

    def test_generate_srt_basic(self):
        """Test basic SRT file generation."""
        generator = SubtitleGenerator()

        segments = [
            TranscriptSegment("第一行字幕", 1.0, 4.5, 1.0),
            TranscriptSegment("第二行字幕", 5.0, 8.75, 1.0),
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            temp_path = f.name

        try:
            output = generator.generate_srt(segments, temp_path)
            assert output == temp_path

            # Read and verify content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for expected SRT structure
            assert "1\n" in content
            assert "00:00:01,000 --> 00:00:04,500" in content
            assert "第一行字幕" in content
            assert "2\n" in content
            assert "00:00:05,000 --> 00:00:08,750" in content
            assert "第二行字幕" in content

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_segments(self):
        """Test handling of empty segment list."""
        generator = SubtitleGenerator()
        merged = generator._merge_short_segments([])
        assert merged == []


class TestTranscriptSegment:
    """Test cases for TranscriptSegment dataclass."""

    def test_segment_creation(self):
        """Test creating a transcript segment."""
        segment = TranscriptSegment(
            text="テストテキスト",
            start_time=1.5,
            end_time=3.7,
            confidence=0.95
        )

        assert segment.text == "テストテキスト"
        assert segment.start_time == 1.5
        assert segment.end_time == 3.7
        assert segment.confidence == 0.95

    def test_segment_default_confidence(self):
        """Test default confidence value."""
        segment = TranscriptSegment(
            text="テスト",
            start_time=0.0,
            end_time=1.0
        )

        assert segment.confidence == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
