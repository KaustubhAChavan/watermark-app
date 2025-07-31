# Watermark Application

Automatically adds watermarks to photos and videos in an INPUT folder. The application monitors the INPUT folder and processes new files automatically, saving watermarked versions to the OUTPUT folder.

## Features

- **Automatic Processing**: Monitors INPUT folder and processes files immediately
- **Multi-format Support**: 
  - Images: JPG, JPEG, PNG, GIF, WebP
  - Videos: MP4, AVI, MOV, WebM, MKV
- **Professional Watermark**: Adds business contact information with customizable styling
- **Robust FFmpeg Integration**: Enhanced text escaping and fallback strategies for video processing
- **Batch Processing**: Handles multiple files efficiently
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Error Handling**: Logs issues and continues processing other files

## Recent Improvements

### FFmpeg Command Syntax Fix

This version includes significant improvements to the video watermarking process:

- **Enhanced Text Escaping**: Properly escapes special characters like colons (`:`) in phone numbers and contact information
- **Multiple Fallback Strategies**: If complex text fails with one escaping method, the system tries alternative approaches
- **Windows Compatibility**: Improved command line handling for better Windows support
- **Better Error Messages**: More descriptive error messages for troubleshooting

The watermark text `"Armstrong Properties\nRavindra Bhubal\ncontact: 7387457889"` now processes correctly without FFmpeg syntax errors.

## Quick Start

1. **Install Python 3.8+ and dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg (for video processing):**
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Add files to process:**
   - Place photos and videos in the `INPUT/` folder
   - Processed files will appear in the `OUTPUT/` folder

### Try the Demo

Run the demo script to see the application in action:
```bash
python demo.py
python app.py
```

This will create sample images and process them automatically.

## Configuration

Edit `config.json` to customize the watermark:

```json
{
  "watermark": {
    "text": "Armstrong Properties\nRavindra Bhubal\ncontact: 7387457889",
    "position": "bottom-right",
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
- `position`: Currently supports "bottom-right"
- `font_size`: Size of the watermark text
- `font_color`: RGB color values [R, G, B] (white = [255, 255, 255])
- `background_color`: RGBA background [R, G, B, Alpha] (semi-transparent black = [0, 0, 0, 128])
- `padding`: Space inside the watermark background
- `margin`: Distance from image/video edge

## Troubleshooting

### FFmpeg Syntax Errors

If you encounter FFmpeg errors with special characters:
- The application automatically tries multiple text escaping strategies
- Check the logs for detailed error messages
- Complex watermark text is automatically handled with fallback methods

### FFmpeg Not Found
If you see "FFmpeg not found" warnings:
1. Install FFmpeg using the instructions above
2. Ensure FFmpeg is in your system PATH
3. Restart the application

## Requirements

- Python 3.8 or higher
- Pillow (PIL) for image processing
- Watchdog for file monitoring
- FFmpeg for video processing (optional but recommended)

## License

This project is open source. Feel free to modify and distribute.
