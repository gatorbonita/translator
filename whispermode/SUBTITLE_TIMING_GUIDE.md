# 🎯 Subtitle Timing & Alignment Guide

## Issue: Multiple Subtitles Overlapping (3 lines on screen)

This happens when:
1. **Segments are too long** (exceed screen width)
2. **Segments overlap in time** (multiple active at once)
3. **Merging is too aggressive** (combining too many segments)

## ✅ Solutions

### Quick Fix 1: Reduce Max Duration & Characters

In **Step 4 (Load Functions)**, find these functions and adjust:

#### Option A: Stricter Limits (Recommended)

```python
def create_segments_from_words(words, max_duration=3.0, max_chars=50):
    """Group words into subtitle segments."""
    # Changed from: max_duration=5.0, max_chars=80
    # To: max_duration=3.0, max_chars=50
```

**And in merge function**:

```python
def merge_short_segments(segments, min_duration=0.8, max_chars=50):
    """Merge segments that are too short."""
    # Changed from: min_duration=1.0, max_chars=80
    # To: min_duration=0.8, max_chars=50
```

#### Option B: Very Short (1-2 Lines Max)

```python
def create_segments_from_words(words, max_duration=2.5, max_chars=40):
    """Group words into subtitle segments."""
    # Very conservative - ensures single line per subtitle
```

```python
def merge_short_segments(segments, min_duration=0.5, max_chars=40):
    """Merge segments that are too short."""
    # Minimal merging - keeps segments short
```

### Quick Fix 2: Add Gap Between Subtitles

Add a new function to ensure gaps between subtitles:

In **Step 4**, add this NEW function after `merge_short_segments`:

```python
def add_gaps_between_subtitles(segments, min_gap=0.2):
    """Ensure minimum gap between consecutive subtitles."""
    if not segments or len(segments) < 2:
        return segments

    adjusted = []

    for i, segment in enumerate(segments):
        current = TranscriptSegment(
            text=segment.text,
            start_time=segment.start_time,
            end_time=segment.end_time,
            confidence=segment.confidence
        )

        # Adjust end time if it overlaps with next segment
        if i < len(segments) - 1:
            next_start = segments[i + 1].start_time
            if current.end_time + min_gap > next_start:
                # Shorten this subtitle to create gap
                current.end_time = next_start - min_gap

                # Make sure end time doesn't go before start time
                if current.end_time <= current.start_time:
                    current.end_time = current.start_time + 0.5

        adjusted.append(current)

    return adjusted
```

**Then in `generate_srt` function**, change:

```python
def generate_srt(segments, output_path):
    """Generate SRT subtitle file."""
    print(f"\n📝 Generating SRT file...")

    # Merge short segments
    merged = merge_short_segments(segments)

    # ADD THIS LINE: Add gaps between subtitles
    adjusted = add_gaps_between_subtitles(merged, min_gap=0.2)

    # Change this line from 'merged' to 'adjusted':
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(adjusted, start=1):  # Changed from 'merged'
            f.write(f"{i}\n")
            start_ts = format_timestamp(segment.start_time)
            end_ts = format_timestamp(segment.end_time)
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{segment.text}\n\n")

    print(f"✅ SRT file created: {output_path}")
    return output_path
```

### Quick Fix 3: Split Long Segments

Add this function to split segments that are too long:

```python
def split_long_segments(segments, max_chars=45):
    """Split segments that are too long to display comfortably."""
    split_segments = []

    for segment in segments:
        if len(segment.text) <= max_chars:
            split_segments.append(segment)
            continue

        # Split long segment
        words = segment.text.split()
        duration = segment.end_time - segment.start_time
        chars_per_second = len(segment.text) / duration if duration > 0 else 1

        current_words = []
        current_start = segment.start_time

        for word in words:
            current_words.append(word)
            current_text = ' '.join(current_words)

            if len(current_text) >= max_chars:
                # Estimate end time based on character count
                chars_count = len(current_text)
                segment_duration = chars_count / chars_per_second
                current_end = min(current_start + segment_duration, segment.end_time)

                split_segments.append(TranscriptSegment(
                    text=current_text,
                    start_time=current_start,
                    end_time=current_end,
                    confidence=segment.confidence
                ))

                current_words = []
                current_start = current_end

        # Add remaining words
        if current_words:
            split_segments.append(TranscriptSegment(
                text=' '.join(current_words),
                start_time=current_start,
                end_time=segment.end_time,
                confidence=segment.confidence
            ))

    return split_segments
```

**Use in `generate_srt`**:

```python
def generate_srt(segments, output_path):
    """Generate SRT subtitle file."""
    print(f"\n📝 Generating SRT file...")

    # Process segments
    merged = merge_short_segments(segments)
    split = split_long_segments(merged, max_chars=45)  # ADD THIS
    adjusted = add_gaps_between_subtitles(split, min_gap=0.2)

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(adjusted, start=1):
            # ... rest of code
```

## 🎯 Complete Optimized Configuration

Here's a **complete replacement** for the relevant functions in Step 4:

```python
def create_segments_from_words(words, max_duration=3.0, max_chars=45):
    """Group words into subtitle segments with optimized timing."""
    segments = []
    current_words = []
    current_start = None
    sentence_endings = {'。', '！', '？', '、'}

    for word in words:
        if current_start is None:
            current_start = word.start

        current_words.append(word.word)
        current_end = word.end
        duration = current_end - current_start
        text = ''.join(current_words).strip()

        should_finalize = False

        # Finalize if duration or length exceeded
        if duration >= max_duration or len(text) >= max_chars:
            should_finalize = True
        # Finalize on sentence endings (but not too short)
        elif any(text.endswith(punct) for punct in sentence_endings):
            if len(text) > 8 or duration > 0.8:
                should_finalize = True

        if should_finalize:
            segments.append(TranscriptSegment(
                text=text,
                start_time=current_start,
                end_time=current_end,
                confidence=1.0
            ))
            current_words = []
            current_start = None

    # Add remaining words
    if current_words:
        text = ''.join(current_words).strip()
        if text:
            segments.append(TranscriptSegment(
                text=text,
                start_time=current_start,
                end_time=current_end,
                confidence=1.0
            ))

    return segments

def merge_short_segments(segments, min_duration=0.8, max_chars=45):
    """Merge segments that are too short."""
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
        time_gap = segment.start_time - current.end_time

        # Merge if current is too short AND combined isn't too long
        should_merge = (
            duration < min_duration and
            len(combined_text) <= max_chars and
            time_gap < 0.5  # Don't merge if there's a big gap
        )

        if should_merge:
            current.text = combined_text
            current.end_time = segment.end_time
        else:
            merged.append(current)
            current = TranscriptSegment(
                text=segment.text,
                start_time=segment.start_time,
                end_time=segment.end_time,
                confidence=segment.confidence
            )

    if current is not None:
        merged.append(current)

    return merged

def add_gaps_between_subtitles(segments, min_gap=0.2, max_duration=4.0):
    """Ensure gaps between subtitles and limit duration."""
    if not segments or len(segments) < 2:
        return segments

    adjusted = []

    for i, segment in enumerate(segments):
        current = TranscriptSegment(
            text=segment.text,
            start_time=segment.start_time,
            end_time=segment.end_time,
            confidence=segment.confidence
        )

        # Limit maximum duration
        duration = current.end_time - current.start_time
        if duration > max_duration:
            current.end_time = current.start_time + max_duration

        # Ensure gap before next subtitle
        if i < len(segments) - 1:
            next_start = segments[i + 1].start_time
            if current.end_time + min_gap > next_start:
                current.end_time = next_start - min_gap

                # Ensure end time is valid
                if current.end_time <= current.start_time:
                    current.end_time = current.start_time + 0.5

        adjusted.append(current)

    return adjusted

def generate_srt(segments, output_path):
    """Generate SRT subtitle file with optimized timing."""
    print(f"\n📝 Generating SRT file...")

    # Apply all optimizations
    print("   Merging short segments...")
    merged = merge_short_segments(segments, min_duration=0.8, max_chars=45)

    print("   Adjusting timing and gaps...")
    adjusted = add_gaps_between_subtitles(merged, min_gap=0.2, max_duration=4.0)

    print(f"   Final subtitle count: {len(adjusted)} (from {len(segments)} original)")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(adjusted, start=1):
            f.write(f"{i}\n")
            start_ts = format_timestamp(segment.start_time)
            end_ts = format_timestamp(segment.end_time)
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{segment.text}\n\n")

    print(f"✅ SRT file created: {output_path}")
    return output_path
```

## 📊 Configuration Comparison

| Setting | Default | Conservative | Aggressive |
|---------|---------|--------------|------------|
| **max_duration** | 5.0s | 3.0s | 2.0s |
| **max_chars** | 80 | 45 | 35 |
| **min_duration** | 1.0s | 0.8s | 0.5s |
| **min_gap** | - | 0.2s | 0.3s |
| **Lines on screen** | 2-3 | 1-2 | 1 |

## 🎬 Best Practices for Subtitles

### Reading Speed
- **Ideal**: 15-20 characters per second
- **Maximum**: 25 characters per second
- **Duration**: 1-6 seconds per subtitle

### Display Rules
- **Max lines**: 2 lines per subtitle
- **Max characters**: 42 per line (84 total)
- **Min duration**: 0.7 seconds
- **Max duration**: 6 seconds
- **Gap between**: 0.2 seconds minimum

### For Anime/Fast Speech
```python
# Optimized for anime:
max_duration=2.5
max_chars=40
min_gap=0.15
```

### For Movies/Slower Speech
```python
# Optimized for movies:
max_duration=4.0
max_chars=50
min_gap=0.2
```

## 🔧 Quick Test Different Settings

Add this cell after generating subtitles to test different configurations:

```python
# TEST DIFFERENT CONFIGURATIONS
from pathlib import Path

configs = [
    {'name': 'Conservative', 'max_dur': 3.0, 'max_chars': 45, 'min_gap': 0.2},
    {'name': 'Aggressive', 'max_dur': 2.5, 'max_chars': 40, 'min_gap': 0.25},
    {'name': 'Very Short', 'max_dur': 2.0, 'max_chars': 35, 'min_gap': 0.3},
]

for config in configs:
    print(f"\nTesting {config['name']} configuration...")

    # Re-process with new settings
    from src.subtitle_generator import SubtitleGenerator
    gen = SubtitleGenerator(
        min_duration=0.8,
        max_chars=config['max_chars']
    )

    output_name = f"{Path(video_filename).stem}_{config['name'].lower()}.srt"
    gen.generate_srt(chinese_segments, output_name)

    print(f"   Created: {output_name}")

print("\nDownload and compare different versions in VLC!")
```

## 💡 Pro Tips

### 1. Test with VLC
- Open video in VLC
- Subtitle → Add Subtitle File
- Try different configurations
- See which looks best

### 2. Adjust in VLC
- Tools → Track Synchronization
- Adjust subtitle delay if needed
- Change subtitle size/position

### 3. Manual Refinement
Use [Subtitle Edit](https://www.nikse.dk/subtitleedit) (free) to:
- Fix timing manually
- Split long subtitles
- Merge short ones
- Auto-adjust reading speed

### 4. Character-based Languages (Chinese/Japanese)
- Use **shorter** max_chars (35-45)
- Characters are denser than English
- Need less space but more time to read

## 🎯 Recommended Settings for Your Case

Based on "3 lines on screen", I recommend:

**In Step 4, change to:**

```python
# In create_segments_from_words:
def create_segments_from_words(words, max_duration=2.5, max_chars=40):

# In merge_short_segments:
def merge_short_segments(segments, min_duration=0.8, max_chars=40):

# Add gaps:
def add_gaps_between_subtitles(segments, min_gap=0.25):
```

This should give you **1-2 lines max** instead of 3!

## 📝 Summary

**Quick fixes (easiest to hardest)**:

1. ✅ Change `max_chars=45` (from 80)
2. ✅ Change `max_duration=3.0` (from 5.0)
3. ✅ Add gaps: `add_gaps_between_subtitles()`
4. ✅ Use complete optimized version above

Try option 1 and 2 first, they're quick parameter changes!
