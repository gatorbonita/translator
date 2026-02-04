# 🐛 Troubleshooting Guide - Whisper Edition

## 🚨 Critical Issue: Incomplete Transcription (FIXED)

### ❌ Problem

**Symptoms:**
- Video is 30 minutes but subtitles only go to ~7 minutes
- Only 32 segments generated (should be 200-400+)
- Transcription stops early without error

**Example:**
```
29.9-minute video → Only 32 segments
Subtitles end at 6:58
No error message
```

### ✅ Solution (v1.1 - Fixed!)

**Root cause**: faster-whisper returns a **generator**, not a list. Once iterated, it's exhausted.

**What was wrong**:
```python
segments, info = model.transcribe(...)  # Returns generator

for segment in segments:  # Iterates and exhausts generator
    ...

# If segments is accessed again anywhere, it's empty!
```

**The fix** (already applied):
```python
segments_generator, info = model.transcribe(...)

# CRITICAL: Convert to list immediately!
segments = list(segments_generator)  # Now it's a real list
print(f"Found {len(segments)} segments")  # Can access multiple times

for segment in segments:  # Works properly
    ...
```

**Status**: ✅ **FIXED in latest version** (Update your notebook/code)

### How to Update

**For Google Colab users**:
1. Go to: https://colab.research.google.com/github/gatorbonita/translator/blob/main/whispermode/Japanese_to_Chinese_Subtitles_Colab.ipynb
2. File → Save a copy in Drive (or just use the latest version)
3. The fix is already included!

**For local users**:
```bash
cd translator
git pull origin main
```

### Verify the Fix

After updating, you should see:
```
✅ Whisper found 247 raw segments covering full audio
```

If you see this, the fix is working! You should now get:
- **200-400+ segments** for a 30-minute video
- **Complete transcription** from start to end
- **Proper segment count**

---

## Other Common Issues

### ❌ Issue: "No GPU detected" in Colab

**Solution**:
1. Runtime → Change runtime type
2. Hardware accelerator: Select **GPU**
3. Click **Save**
4. Runtime → Restart runtime
5. Run all cells again

**Verify GPU**:
```python
import torch
print(torch.cuda.is_available())  # Should print: True
```

### ❌ Issue: "Out of memory"

**Symptoms**:
- OOM error during transcription
- Colab crashes
- "CUDA out of memory"

**Solutions**:

1. **Use smaller model**:
   ```python
   WHISPER_MODEL = 'small'  # Instead of 'medium' or 'large-v3'
   ```

2. **Restart runtime**:
   - Runtime → Factory reset runtime
   - Run all cells again

3. **Reduce batch size** (for very long videos):
   - Edit transcribe function
   - Process in chunks

4. **Use CPU** (slower but works):
   ```python
   DEVICE = 'cpu'
   ```

### ❌ Issue: Slow transcription on CPU

**Symptoms**:
- 30-minute video takes 30+ minutes to process
- "Using CPU" message shown

**Solutions**:

1. **Enable GPU** (see above)

2. **Use smaller model**:
   ```python
   WHISPER_MODEL = 'small'  # Faster, still good quality
   ```

3. **For local install**, use GPU:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### ❌ Issue: Translation fails

**Symptoms**:
- Error during translation step
- "401 Unauthorized" or "403 Forbidden"

**Solutions**:

1. **Check credentials uploaded**:
   - In Colab, make sure JSON file uploaded in Step 2
   - Check filename matches

2. **Verify API enabled**:
   - Go to: https://console.cloud.google.com
   - Check "Cloud Translation API" is enabled

3. **Check service account permissions**:
   - Service account needs: "Cloud Translation API User" role

4. **Test without translation**:
   ```python
   SKIP_TRANSLATION = True
   ```
   This will test transcription only

### ❌ Issue: Video upload fails

**Symptoms**:
- Upload stalls or fails
- File >100MB won't upload

**Solutions**:

1. **Use Google Drive** (for large files):
   ```python
   # Replace upload cell with:
   from google.colab import drive
   drive.mount('/content/drive')

   video_path = '/content/drive/MyDrive/your-video.mp4'
   video_filename = 'your-video.mp4'
   ```

2. **Compress video** first:
   - Lower resolution (720p instead of 1080p)
   - Use handbrake or ffmpeg

3. **Split video** into shorter segments:
   ```bash
   ffmpeg -i long.mp4 -t 00:30:00 part1.mp4  # First 30 min
   ffmpeg -i long.mp4 -ss 00:30:00 part2.mp4  # Rest
   ```

### ❌ Issue: Poor transcription quality

**Symptoms**:
- Many incorrect words
- Missing dialogue
- Gibberish text

**Solutions**:

1. **Use larger model**:
   ```python
   WHISPER_MODEL = 'large-v3'  # Best quality
   ```

2. **Check audio quality**:
   - Is audio clear?
   - Is it actually Japanese?
   - Remove background music if possible

3. **Adjust VAD settings** (Voice Activity Detection):
   ```python
   # In transcribe_with_whisper function, change:
   vad_parameters=dict(min_silence_duration_ms=1000)  # Less aggressive
   # Or disable VAD:
   vad_filter=False
   ```

4. **Try without VAD**:
   - Sometimes VAD removes speech accidentally
   - Edit function, set `vad_filter=False`

### ❌ Issue: Subtitles too short/long

**Symptoms**:
- Subtitles flash too quickly
- Subtitles stay too long

**Solutions**:

1. **Adjust segment merging**:
   ```python
   # In merge_short_segments function:
   def merge_short_segments(segments, min_duration=1.5, max_chars=80):
       # Change min_duration: 1.5 instead of 1.0
   ```

2. **Adjust in SRT editor**:
   - Use Subtitle Edit (free tool)
   - Adjust timing after generation

### ❌ Issue: Wrong language detected

**Symptoms**:
- "Detected language: en" (but video is Japanese)
- Transcription in wrong language

**Solutions**:

1. **Force language**:
   ```python
   # In transcribe_with_whisper, language is already set to 'ja'
   # Make sure this line exists:
   language='ja',  # Force Japanese
   ```

2. **Check audio track**:
   - Is the right audio track extracted?
   - Some videos have multiple audio tracks

### ❌ Issue: Colab session disconnects

**Symptoms**:
- Processing stops mid-way
- "Runtime disconnected" message

**Solutions**:

1. **Colab timeout** (free tier limits):
   - ~12 hours max session
   - Download subtitle immediately when done

2. **Keep browser active**:
   - Don't close tab
   - Don't let computer sleep

3. **For very long videos**:
   - Use local installation instead
   - Or split video into parts

### ❌ Issue: Segments out of order

**Symptoms**:
- Subtitle timing is wrong
- Segments appear in wrong order

**Solution**:
- This should be fixed with the generator fix above
- If still happening, report as bug

### ❌ Issue: Missing punctuation

**Symptoms**:
- No periods, commas in Japanese text
- Run-on sentences

**Solution**:
- Already enabled: `enable_automatic_punctuation=True`
- This is a Whisper model limitation
- Manual editing may be needed

### ❌ Issue: Special characters broken

**Symptoms**:
- Chinese characters show as �����
- Encoding errors

**Solution**:
- This should be fixed (using UTF-8)
- If still happening, check:
  ```python
  with open(output_path, 'w', encoding='utf-8') as f:
  ```

## 🆘 Still Having Issues?

### Before Reporting:

1. ✅ Updated to latest version
2. ✅ Enabled GPU in Colab
3. ✅ Used recommended settings
4. ✅ Checked error messages carefully
5. ✅ Tried troubleshooting steps above

### Report a Bug:

If none of the above helps:

1. **GitHub Issues**: https://github.com/gatorbonita/translator/issues
2. **Include**:
   - Error message (copy full text)
   - What you tried
   - Video length
   - Model used
   - GPU or CPU
   - Colab or local

### Useful Debug Info:

```python
# Run this in a Colab cell for debug info:
print("System Info:")
print(f"  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
print(f"  Model: {WHISPER_MODEL}")
print(f"  Video duration: {duration:.1f}s")
print(f"  Segments found: {len(segments)}")
print(f"  First segment: {segments[0] if segments else 'None'}")
print(f"  Last segment: {segments[-1] if segments else 'None'}")
```

## ✅ Verification Checklist

After processing, verify:

- [ ] Subtitle count: ~7-12 segments per minute of video
- [ ] Time range: Covers full video length
- [ ] First subtitle: Starts near beginning (~0:00:01)
- [ ] Last subtitle: Ends near video end
- [ ] Text quality: Readable Chinese (if translated)
- [ ] File size: .srt file is >1KB (not empty)

**Example for 30-min video:**
- ✅ **200-360 segments**
- ✅ Time: **00:00:01** to **00:29:58**
- ✅ File size: **15-30 KB**

If your output matches this, it's working correctly!

---

## 📚 Additional Resources

- **Colab Guide**: [COLAB_GUIDE.md](COLAB_GUIDE.md)
- **Full Documentation**: [README.md](README.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **GitHub**: [gatorbonita/translator](https://github.com/gatorbonita/translator)

---

<div align="center">

**🎉 Most issues are now fixed in v1.1!**

Update your code and try again.

</div>
