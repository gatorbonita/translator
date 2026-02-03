# Chinese Subtitle Generator for Japanese Movies

A Python CLI tool that automatically generates Chinese subtitles for Japanese language videos using Google Cloud Speech-to-Text and Translate APIs.

## Features

- 🎬 Extract audio from any video format (MP4, MKV, AVI, etc.)
- 🎤 Transcribe Japanese audio to text with precise timestamps
- 🌏 Translate Japanese text to Chinese (Simplified or Traditional)
- 📝 Generate standard SRT subtitle files
- ⚡ Optimized processing with batch translation
- 🔄 Automatic retry logic for API failures
- 📊 Detailed logging and progress tracking

## How It Works

```
Video File → Audio Extraction → Speech Recognition → Translation → SRT Generation
   (MP4)        (WAV 16kHz)      (Japanese text)    (Chinese text)   (subtitles)
```

## Prerequisites

1. **Python 3.8 or higher**
2. **Google Cloud Account** with:
   - Cloud Speech-to-Text API enabled
   - Cloud Translation API enabled
   - Service account with appropriate permissions

## Installation

### 1. Clone or Download

```bash
cd translator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Google Cloud Credentials

#### Create Service Account:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable APIs:
   - Go to "APIs & Services" → "Library"
   - Enable "Cloud Speech-to-Text API"
   - Enable "Cloud Translation API"
4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Grant roles:
     - "Cloud Speech Client"
     - "Cloud Translation API User"
   - Create JSON key and download

#### Configure Credentials:

**Option 1: Environment Variable (Recommended)**
```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Windows (Command Prompt)
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json

# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

**Option 2: .env File**
```bash
cp .env.example .env
# Edit .env and set GOOGLE_APPLICATION_CREDENTIALS path
```

**Option 3: Command Line**
```bash
python main.py video.mp4 --credentials /path/to/key.json
```

## Usage

### Basic Usage

```bash
# Generate subtitles (output: video_name.srt)
python main.py movie.mp4
```

### Advanced Usage

```bash
# Specify output path
python main.py movie.mp4 -o subtitles/movie_ch.srt

# Use Traditional Chinese instead of Simplified
python main.py movie.mp4 --target-lang zh-TW

# Enable verbose logging
python main.py movie.mp4 --verbose

# Keep temporary audio files (for debugging)
python main.py movie.mp4 --keep-temp

# Specify credentials file
python main.py movie.mp4 --credentials /path/to/key.json
```

### Command-Line Options

```
Options:
  -o, --output PATH          Output SRT file path
  -c, --credentials PATH     Google Cloud credentials JSON file
  --keep-temp               Keep temporary audio files
  -v, --verbose             Enable verbose logging
  --target-lang [zh-CN|zh-TW]  Target Chinese variant (default: zh-CN)
  --help                    Show help message
```

## Example

```bash
$ python main.py anime_episode.mp4 --verbose
============================================================
Chinese Subtitle Generator for Japanese Movies
============================================================
2024-01-15 10:30:00 | INFO     | Input video: anime_episode.mp4
2024-01-15 10:30:00 | INFO     | Output subtitle: anime_episode.srt
2024-01-15 10:30:00 | INFO     | Target language: zh-CN
------------------------------------------------------------
2024-01-15 10:30:00 | INFO     | Step 1/5: Validating video file...
2024-01-15 10:30:00 | SUCCESS  | Video file validated
2024-01-15 10:30:00 | INFO     | Step 2/5: Extracting audio from video...
2024-01-15 10:30:15 | SUCCESS  | Audio extracted: 24m 35s
2024-01-15 10:30:15 | INFO     | Step 3/5: Transcribing Japanese audio to text...
2024-01-15 10:55:20 | SUCCESS  | Transcription complete: 342 segments
2024-01-15 10:55:20 | INFO     | Step 4/5: Translating Japanese to Chinese...
2024-01-15 10:55:25 | SUCCESS  | Translation complete: 342 segments
2024-01-15 10:55:25 | INFO     | Step 5/5: Generating SRT subtitle file...
2024-01-15 10:55:25 | SUCCESS  | Subtitle file created: anime_episode.srt
============================================================
SUBTITLE GENERATION COMPLETE!
Video duration: 24m 35s
Subtitle segments: 298
Output file: anime_episode.srt
============================================================
```

## Output Format

The tool generates standard SRT (SubRip) subtitle files:

```srt
1
00:00:01,000 --> 00:00:04,500
这是第一行字幕

2
00:00:05,000 --> 00:00:08,750
这是第二行字幕

3
00:00:09,200 --> 00:00:12,800
字幕会自动合并以提高可读性
```

## Supported Video Formats

- MP4
- MKV
- AVI
- MOV
- WMV
- FLV
- WebM
- M4V
- MPG/MPEG
- 3GP

## Performance

- **Processing Time**: Approximately 1:1 ratio (1-hour video ≈ 1 hour processing)
- **Bottleneck**: Google Speech-to-Text API transcription
- **Memory Usage**: < 500MB for typical movies

## Cost Estimation

**Google Cloud Pricing (as of 2024):**

- **Speech-to-Text**: $0.006 per 15 seconds of audio
  - 2-hour movie: ~$11.52
  - 30-minute video: ~$2.88

- **Translation**: $20 per 1 million characters
  - 2-hour movie (~50,000 chars): ~$1.00
  - 30-minute video (~12,500 chars): ~$0.25

**Total Cost Examples:**
- 30-minute anime episode: ~$3.13
- 2-hour movie: ~$12.52

> Free tier: Google Cloud offers $300 free credit for new accounts

## Troubleshooting

### Error: "Credentials not found"

**Solution**: Set GOOGLE_APPLICATION_CREDENTIALS environment variable or use --credentials flag

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Error: "API not enabled"

**Solution**: Enable required APIs in Google Cloud Console:
- Cloud Speech-to-Text API
- Cloud Translation API

### Error: "Permission denied"

**Solution**: Ensure service account has required roles:
- "Cloud Speech Client"
- "Cloud Translation API User"

### Error: "Quota exceeded"

**Solution**:
- Check your Google Cloud quota limits
- Wait for quota to reset (usually daily)
- Request quota increase in Google Cloud Console

### Poor Translation Quality

**Tips**:
- Ensure audio is clear (no background noise)
- Try Traditional Chinese (--target-lang zh-TW) if Simplified doesn't work well
- Manual post-editing may be needed for complex terminology

## Project Structure

```
translator/
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env.example            # Environment template
├── config/
│   └── settings.py         # Configuration management
├── src/
│   ├── audio_extractor.py      # Audio extraction with MoviePy
│   ├── speech_recognizer.py    # Google Speech-to-Text
│   ├── translator.py           # Google Translate
│   ├── subtitle_generator.py   # SRT generation
│   └── utils.py               # Utilities & exceptions
├── tests/
│   └── test_*.py          # Unit tests
├── logs/                  # Application logs
└── temp/                  # Temporary audio files
```

## Development

### Running Tests

```bash
pytest tests/
```

### Running with Debug Logging

```bash
python main.py video.mp4 --verbose
```

Logs are saved to `logs/subtitle_generator.log`

## Technical Details

### Audio Processing
- **Format**: WAV (LINEAR16 encoding)
- **Sample Rate**: 16kHz (optimal for speech)
- **Channels**: Mono (1 channel)

### Speech Recognition
- **Language**: Japanese (ja-JP)
- **Features**:
  - Word-level timestamps
  - Automatic punctuation
  - Synchronous API for short videos (< 60s)
  - Long-running API for longer videos (up to 8 hours)

### Translation
- **Source**: Japanese (ja)
- **Target**: Chinese Simplified (zh-CN) or Traditional (zh-TW)
- **Batch Size**: 128 segments per API call

### Subtitle Generation
- **Format**: SRT (SubRip)
- **Segment Duration**: 1-5 seconds
- **Max Characters**: 80 per subtitle line
- **Auto-merge**: Short segments merged for readability

## Limitations

- Requires internet connection for Google APIs
- Processing time is approximately equal to video length
- Translation quality depends on audio clarity
- Japanese-specific: Only works for Japanese audio
- API costs apply (see Cost Estimation section)

## License

This project is provided as-is for educational and personal use.

## Acknowledgments

- Google Cloud Speech-to-Text API
- Google Cloud Translation API
- MoviePy for video processing
- Click for CLI framework
- Loguru for logging

## Support

For issues and questions:
1. Check the Troubleshooting section
2. Review Google Cloud API documentation
3. Check application logs in `logs/` directory

## Contributing

Contributions are welcome! Areas for improvement:
- Support for more languages
- GUI interface
- Batch processing multiple videos
- Cloud Storage integration for large files
- Advanced subtitle formatting options

---

**Made with ❤️ for the anime and movie community**
