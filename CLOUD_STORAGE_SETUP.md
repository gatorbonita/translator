# Google Cloud Storage Setup for Large Videos

## When Do You Need This?

If you see an error like:
```
ERROR: 400 request payload size exceeds the limit: 10485760 bytes
```

This means your video's audio is larger than 10MB. You need to set up Google Cloud Storage to handle large files.

## Setup Steps

### 1. Create a Cloud Storage Bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Storage** → **Buckets**
3. Click **"Create Bucket"**
4. Configure:
   - **Name**: Choose a unique name (e.g., `my-subtitle-generator-bucket`)
   - **Location type**: Region (choose closest to you)
   - **Storage class**: Standard
   - **Access control**: Uniform
   - **Public access**: **Prevent public access** (keep default)
5. Click **"Create"**

### 2. Grant Bucket Permissions to Service Account

1. Go to your bucket's details page
2. Click the **"Permissions"** tab
3. Click **"Grant Access"**
4. Add your service account email (looks like: `your-sa@your-project.iam.gserviceaccount.com`)
5. Assign roles:
   - `Storage Object Admin` (to create/delete objects)
6. Click **"Save"**

### 3. Configure the Application

**Option 1: Environment Variable**

```bash
# Linux/Mac
export GCS_BUCKET_NAME="your-bucket-name"

# Windows (Command Prompt)
set GCS_BUCKET_NAME=your-bucket-name

# Windows (PowerShell)
$env:GCS_BUCKET_NAME="your-bucket-name"
```

**Option 2: .env File**

Add to your `.env` file:
```
GCS_BUCKET_NAME=your-bucket-name
```

### 4. Run the Application Again

```bash
python main.py your-large-video.mp4
```

The application will automatically:
1. Detect that audio file is > 10MB
2. Upload it to your Cloud Storage bucket
3. Process the transcription
4. Delete the temporary file from Cloud Storage

## Cost Considerations

**Cloud Storage Pricing:**
- Storage: $0.020 per GB per month
- Operations: $0.05 per 10,000 operations

**For subtitle generation:**
- Typical audio file: 50-200 MB
- Stored for: < 1 hour (then deleted)
- **Cost per video**: < $0.01 (essentially free)

## Troubleshooting

### Error: "Bucket not found"

**Cause**: Bucket name is incorrect or doesn't exist

**Solution**: Verify bucket name in Cloud Console

### Error: "Permission denied"

**Cause**: Service account doesn't have access to the bucket

**Solution**: Grant `Storage Object Admin` role to your service account

### Error: "Bucket name already exists"

**Cause**: Bucket names are globally unique across all Google Cloud

**Solution**: Choose a different, unique bucket name

## Security Notes

- Temporary audio files are automatically deleted after processing
- Keep your bucket private (prevent public access)
- Only your service account needs access
- Audio files are stored for < 1 hour during processing

## Alternative: Split Long Videos

If you don't want to use Cloud Storage, you can split your video into shorter segments:

```bash
# Using FFmpeg
ffmpeg -i long-video.mp4 -t 00:10:00 part1.mp4
ffmpeg -i long-video.mp4 -ss 00:10:00 -t 00:10:00 part2.mp4

# Then process each part
python main.py part1.mp4
python main.py part2.mp4
```

Then manually combine the SRT files.
