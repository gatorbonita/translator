# 🚀 Google Colab Guide - FREE GPU Subtitle Generation

## 🎯 What is This?

A **Jupyter notebook** that runs in Google Colab with **FREE GPU access**. Perfect for generating Chinese subtitles without any local installation!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gatorbonita/translator/blob/main/whispermode/Japanese_to_Chinese_Subtitles_Colab.ipynb)

## ✨ Why Use Colab?

### Perfect For:
✅ **Beginners** - No Python installation needed
✅ **No GPU?** - Use Google's free GPU (much faster than CPU)
✅ **Quick processing** - 30-min video in ~3-5 minutes
✅ **Zero setup** - Everything runs in your browser
✅ **Free** - Completely free to use

### Comparison:

| Feature | Google Colab | Local CPU | Local GPU |
|---------|-------------|-----------|-----------|
| **Setup Time** | 0 minutes | 10-15 minutes | 15-30 minutes |
| **Cost** | FREE | FREE | FREE (if you have GPU) |
| **30-min Video** | ~3-5 minutes | ~15-20 minutes | ~3-5 minutes |
| **Installation** | None | Python + packages | Python + packages + CUDA |

## 🚀 Quick Start (5 Minutes)

### Step 1: Open Notebook

Click the badge: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gatorbonita/translator/blob/main/whispermode/Japanese_to_Chinese_Subtitles_Colab.ipynb)

### Step 2: Enable GPU

1. Click **Runtime** → **Change runtime type**
2. Select **GPU** from "Hardware accelerator" dropdown
3. Click **Save**

![Enable GPU](https://i.imgur.com/YqS5D5r.png)

### Step 3: Run All Cells

1. Click **Runtime** → **Run all** (or press `Ctrl+F9`)
2. Wait for setup (~2-3 minutes first time)
3. Upload your credentials when prompted (optional for testing)
4. Upload your video file
5. Wait for processing (~3-5 minutes for 30-min video)
6. Download your .srt file!

## 📋 Detailed Walkthrough

### Cell 1: Setup Environment

**What it does**: Checks for GPU, installs packages

**Time**: ~2-3 minutes first time, <30 seconds after

**Output**:
```
✅ GPU detected: Tesla T4
   VRAM: 15.0 GB
✅ Setup complete!
```

### Cell 2: Upload Credentials

**What it does**: Uploads your Google Cloud credentials for translation

**Options**:
- **With credentials**: Full translation to Chinese
- **Without credentials**: Skip translation, get Japanese transcript only

**How to get credentials**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable "Cloud Translation API"
3. Create Service Account → Download JSON key
4. Upload that JSON file

**Testing without credentials**: Set `SKIP_TRANSLATION = True`

### Cell 3: Configuration

**What it does**: Set your preferences

**Options**:
- `WHISPER_MODEL`:
  - `'small'` = Fast, good quality
  - `'medium'` = **Recommended** - Best balance
  - `'large-v3'` = Best quality, slower
- `TARGET_LANGUAGE`:
  - `'zh-CN'` = Simplified Chinese (default)
  - `'zh-TW'` = Traditional Chinese
- `DEVICE`:
  - `'auto'` = **Recommended** - Uses GPU if available

### Cell 4: Load Functions

**What it does**: Loads all the processing code

**Time**: <10 seconds

### Cell 5: Upload Video

**What it does**: Upload your Japanese video

**Supported formats**: MP4, MKV, AVI, MOV, WebM, FLV, etc.

**Tips**:
- Files >100MB may be slow to upload
- For large files, use Google Drive (see advanced section)
- Maximum file size: ~5GB (Colab limit)

### Cell 6: Process Video ⭐

**What it does**: The main processing!

**Steps**:
1. 🎵 Extract audio (~30 seconds)
2. 🎤 Transcribe with Whisper (~2-4 minutes)
3. 🌏 Translate to Chinese (~10 seconds)
4. 📝 Generate SRT file (~5 seconds)

**Total time** (30-min video with GPU):
- Audio extraction: ~30 seconds
- Whisper transcription: ~2-4 minutes
- Translation: ~10 seconds
- **Total: ~3-5 minutes**

**Output**:
```
🎉 SUBTITLE GENERATION COMPLETE!
Video duration: 1475.5 seconds (24.6 minutes)
Processing time: 182.3 seconds (3.0 minutes)
Segments: 298
Model: medium
```

### Cell 7: Download Subtitle

**What it does**: Downloads the .srt file to your computer

**Output**: `your-video_zh-CN.srt` or `your-video_ja.srt` (if no translation)

### Cell 8: Preview (Optional)

**What it does**: Shows first 10 subtitles

**Example**:
```
1
00:00:01,000 --> 00:00:04,500
这是第一行字幕

2
00:00:05,000 --> 00:00:08,750
这是第二行字幕
```

## 🎓 Advanced Usage

### Use Google Drive for Large Files

Instead of uploading, use files from Google Drive:

```python
# In Cell 5, replace upload with:
from google.colab import drive
drive.mount('/content/drive')

video_path = '/content/drive/MyDrive/your-video.mp4'
video_filename = 'your-video.mp4'
```

### Batch Processing Multiple Videos

Process multiple videos in one session:

```python
# In Cell 5, add a loop:
video_files = [
    '/content/drive/MyDrive/video1.mp4',
    '/content/drive/MyDrive/video2.mp4',
    '/content/drive/MyDrive/video3.mp4'
]

for video_path in video_files:
    video_filename = os.path.basename(video_path)
    # Run Cell 6 code here
```

### Save to Google Drive Instead of Download

```python
# After Cell 6, add:
from shutil import copy
copy(SUBTITLE_FILE, f'/content/drive/MyDrive/subtitles/{os.path.basename(SUBTITLE_FILE)}')
```

## 🐛 Troubleshooting

### ❌ "No GPU detected"

**Solution**:
1. Runtime → Change runtime type
2. Select "GPU"
3. Click Save
4. Runtime → Restart runtime
5. Run all cells again

### ❌ "Out of memory"

**Solutions**:
1. Use smaller model:
   ```python
   WHISPER_MODEL = 'small'  # or 'base'
   ```
2. Runtime → Factory reset runtime
3. Try again

### ❌ "Translation error"

**Check**:
1. Credentials file uploaded correctly
2. Cloud Translation API is enabled in Google Cloud
3. Service account has "Cloud Translation API User" role

**Workaround**: Set `SKIP_TRANSLATION = True` to test transcription only

### ❌ "Upload fails for large files"

**Solutions**:
1. Use Google Drive method (see Advanced Usage)
2. Compress video first (lower resolution)
3. Split video into smaller segments

### ❌ "Runtime disconnected"

**Reason**: Colab free tier has session limits (~12 hours)

**Solution**:
- Save subtitle file immediately
- For long videos, use local installation

## 💡 Tips & Best Practices

### For Best Results:

1. **Always enable GPU** - Runtime → Change runtime type → GPU
2. **Use medium model** - Best balance for most videos
3. **Test with short clip first** - Upload 5-min clip to verify quality
4. **Upload credentials** - Get full Chinese translation
5. **Download immediately** - Don't lose your work if session ends

### Model Selection Guide:

| Video Type | Recommended Model | Why |
|-----------|------------------|-----|
| Anime (24 min) | `medium` | Best quality for this length |
| Movie (2 hours) | `small` or `medium` | Balance speed and quality |
| Short clip (< 5 min) | `large-v3` | Can afford slower processing |
| Testing | `small` or `base` | Quick results |

### GPU Usage Limits:

- **Free tier**: ~12 hours per session
- **Cool down**: May need to wait if hitting limits
- **Best practice**: Process one video at a time

## 📊 Performance Expectations

### Processing Times (GPU - Tesla T4):

| Video Length | Model | Time |
|-------------|-------|------|
| 5 minutes | small | ~45 seconds |
| 5 minutes | medium | ~1 minute |
| 5 minutes | large-v3 | ~2 minutes |
| 30 minutes | small | ~2 minutes |
| 30 minutes | medium | ~3-4 minutes |
| 30 minutes | large-v3 | ~8-10 minutes |
| 2 hours | small | ~8-10 minutes |
| 2 hours | medium | ~15-20 minutes |
| 2 hours | large-v3 | ~40-50 minutes |

### Quality Comparison:

| Aspect | small | medium | large-v3 |
|--------|-------|--------|----------|
| Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| VRAM | 2GB | 5GB | 10GB |

**Recommendation**: Use `medium` for 95% of use cases.

## 🔒 Privacy & Security

### Data Privacy:

- **Your video**: Processed in your Colab session, not stored by us
- **Audio files**: Temporary, deleted after processing
- **Transcripts**: Only you have access
- **Google Translate**: Audio is NOT sent, only text segments

### Best Practices:

1. Don't share your credentials file
2. Delete sensitive files after processing
3. Use Google Drive for private videos (requires mounting)

## 📚 Additional Resources

- **Full Documentation**: [whispermode/README.md](README.md)
- **Local Installation**: [QUICK_START.md](QUICK_START.md)
- **Version Comparison**: [WHISPER_VS_GOOGLE.md](../WHISPER_VS_GOOGLE.md)
- **GitHub Repository**: [gatorbonita/translator](https://github.com/gatorbonita/translator)

## 🆘 Still Need Help?

1. **Read error messages carefully** - They usually tell you what's wrong
2. **Check notebook cells** - Look for ❌ or warning messages
3. **Review this guide** - Most issues are covered here
4. **Check GitHub Issues**: [Report a bug](https://github.com/gatorbonita/translator/issues)

---

<div align="center">

## 🎉 Ready to Start?

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gatorbonita/translator/blob/main/whispermode/Japanese_to_Chinese_Subtitles_Colab.ipynb)

**Click above to begin generating subtitles in 5 minutes!**

Made with ❤️ using Whisper + Google Translate + Colab

</div>
