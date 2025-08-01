# Watermark Application

Comprehensive watermarking application that handles both photos and videos with advanced features including audio integration and animated watermarks.

## Features

### Image Watermarking
- **Centered Watermarks**: Watermarks are positioned in the center and centrally aligned on images
- **Multi-format Support**: JPG, JPEG, PNG, GIF, WebP
- **Separate Input/Output Folders**: Dedicated folders for image processing

### Video Watermarking  
- **Animated Watermarks**: Watermark moves from center top to bottom throughout the video
- **Audio Integration**: Automatically adds audio from separate audio input folder
- **Audio Replacement**: Removes existing video audio and replaces with selected audio
- **Audio Looping**: If video is longer than audio, loops audio seamlessly to match video duration
- **Multi-format Support**: MP4, AVI, MOV, WebM, MKV
- **Separate Input/Output Folders**: Dedicated folders for video processing

### Audio Processing
- **Dedicated Audio Folder**: Separate input folder for audio files
- **Format Support**: MP3, WAV, AAC, OGG, M4A
- **Automatic Matching**: Matches audio files to videos by filename (falls back to first available audio)
- **Seamless Looping**: Audio loops automatically to cover full video duration

## Folder Structure

The application uses a clear folder structure to organize different media types:

```
input_images/   - Place images here for watermarking
output_images/  - Watermarked images will appear here
input_videos/   - Place videos here for watermarking  
output_videos/  - Watermarked videos will appear here
input_audio/    - Place audio files here for video audio replacement
```

## Quick Start

1. **Install Python 3.8+ and dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg (required for video processing):**
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Add files to process:**
   - Place images in the `input_images/` folder
   - Place videos in the `input_videos/` folder  
   - Place audio files in the `input_audio/` folder
   - Processed files will appear in their respective output folders

### Try the Demo

Run the demo script to see the application in action:
```bash
python demo.py
python app.py
```

This will create sample images, videos, and audio files, then process them automatically.

## Configuration

Edit `config.json` to customize the watermark:

```json
{
  "watermark": {
    "text": "Armstrong Properties\nRavindra Bhubal\ncontact: 7387457889",
    "image_position": "center",
    "video_animation": "top-to-bottom",
    "font_size": 24,
    "font_color": [255, 255, 255],
    "background_color": [0, 0, 0, 128],
    "padding": 20,
    "margin": 30
  }
}
```

### Watermark Options

- `text`: Multi-line watermark text (use `\n` for new lines)
- `image_position`: Position for image watermarks ("center")
- `video_animation`: Animation style for video watermarks ("top-to-bottom")
- `font_size`: Size of the watermark text
- `font_color`: RGB color values [R, G, B] (white = [255, 255, 255])
- `background_color`: RGBA background [R, G, B, Alpha] (semi-transparent black = [0, 0, 0, 128])
- `padding`: Space inside the watermark background
- `margin`: Distance from image/video edge

## Technical Features

- **Automatic Processing**: Monitors input folders and processes files immediately
- **Professional Quality**: Maintains high quality during processing
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Error Handling**: Comprehensive logging and error recovery
- **Efficient Processing**: Optimized for batch processing multiple files

## Audio-Video Synchronization

- Videos are automatically matched with audio files by filename
- If no exact match is found, the first available audio file is used
- Audio automatically loops to match the full video duration
- Original video audio is completely replaced
- Supports seamless audio looping without gaps or clicks

## Requirements

- Python 3.8 or higher
- Pillow (PIL) for image processing
- Watchdog for file monitoring
- FFmpeg for video and audio processing (required)

## License

This project is open source. Feel free to modify and distribute.
