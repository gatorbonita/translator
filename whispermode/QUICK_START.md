# ⚡ Quick Start Guide - Whisper Edition

## 🎯 What You Need (5 Minutes Setup)

1. ✅ **Python 3.8+** (check: `python --version`)
2. ✅ **Google Cloud Translation credentials** (only for translation, NOT transcription)
3. ✅ **Your video file**

## 🚀 Three Steps to Subtitles

### Step 1: Install (First Time Only)

```bash
cd whispermode
pip install -r requirements.txt
```

⏱️ **Time**: 2-3 minutes
📦 **Downloads**: ~100MB of packages

**Note**: Whisper model (~1-3GB) will download automatically on first run.

### Step 2: Set Translation Credentials

```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your-key.json"

# Windows CMD
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your-key.json

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
```

**Don't have credentials?** Quick setup:
1. Go to https://console.cloud.google.com
2. Enable "Cloud Translation API"
3. Create service account → Download JSON key

### Step 3: Generate Subtitles!

```bash
python main.py your-video.mp4
```

⏱️ **Processing Time**:
- 30-min video with GPU: ~3-5 minutes
- 30-min video with CPU: ~15-20 minutes

**Done!** Your subtitle file: `your-video.srt`

## 🎬 Test It

Open in VLC:
1. Open your video
2. Subtitle → Add Subtitle File
3. Select the .srt file
4. Enjoy! 🎉

## ⚙️ Common Options

```bash
# Best quality (slower)
python main.py video.mp4 --whisper-model large-v3

# Faster processing
python main.py video.mp4 --whisper-model small

# Traditional Chinese
python main.py video.mp4 --target-lang zh-TW

# Custom output
python main.py video.mp4 -o subtitles/movie.srt

# See all options
python main.py --help
```

## 💡 First-Time Tips

1. **Test with a short clip first** (5-10 minutes)
2. **Start with medium model** (default)
3. **Check your GPU** - runs much faster with GPU
4. **Be patient on first run** - model download takes time

## 🐛 Quick Fixes

**"No module named 'faster_whisper'"**
```bash
pip install -r requirements.txt
```

**"Credentials not found"**
```bash
# Set the environment variable (see Step 2 above)
```

**"Slow on CPU"**
```bash
# Use smaller model
python main.py video.mp4 --whisper-model small
```

**"GPU not working"**
```bash
# Install CUDA PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 📊 What to Expect

### Quality
- **Whisper transcription**: ⭐⭐⭐⭐⭐ (Much better than Google!)
- **Google Translation**: ⭐⭐⭐⭐

### Cost
- **Transcription**: FREE (runs locally)
- **Translation**: ~$1 per 2-hour movie

### Speed (30-min video, medium model)
- **RTX 3060**: ~3 minutes
- **GTX 1660**: ~5 minutes
- **Intel i7**: ~15 minutes
- **Intel i5**: ~20 minutes

## 🎓 Model Guide

| Model | Best For | Quality | Speed |
|-------|----------|---------|-------|
| **small** | Quick tests, older PCs | Good | Fast |
| **medium** | Most users (default) | Excellent | Moderate |
| **large-v3** | Best quality | Best | Slower |

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Google Cloud credentials set up
- [ ] Video file ready
- [ ] Run: `python main.py your-video.mp4`
- [ ] Test subtitle file in VLC

## 🆘 Need Help?

1. Check the full [README.md](README.md) for detailed docs
2. Review error messages carefully
3. Check `logs/subtitle_generator.log` for details
4. Ensure Google Cloud Translation API is enabled

---

**Ready? Let's go!**

```bash
python main.py your-first-video.mp4
```

🎉 **Enjoy much better subtitle quality with Whisper!**
