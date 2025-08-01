#!/usr/bin/env python3
"""
Watermark Application
Automatically adds watermarks to photos and videos in the INPUT folder.
"""

import os
import sys
import json
import logging
import shutil
import subprocess
from pathlib import Path
from threading import Lock
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watermark_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WatermarkProcessor:
    def __init__(self, config_path='config.json'):
        """Initialize the watermark processor with configuration."""
        self.config = self.load_config(config_path)
        self.processing_lock = Lock()
        self.setup_directories()
        
    def load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def setup_directories(self):
        """Create INPUT and OUTPUT directories if they don't exist."""
        input_dir = Path(self.config['folders']['input'])
        output_dir = Path(self.config['folders']['output'])
        
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Input directory: {input_dir.absolute()}")
        logger.info(f"Output directory: {output_dir.absolute()}")
    
    def is_supported_file(self, file_path):
        """Check if file is a supported format."""
        suffix = Path(file_path).suffix.lower()
        supported = (
            self.config['supported_formats']['images'] + 
            self.config['supported_formats']['videos']
        )
        return suffix in supported
    
    def is_image_file(self, file_path):
        """Check if file is a supported image format."""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.config['supported_formats']['images']
    
    def is_video_file(self, file_path):
        """Check if file is a supported video format."""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.config['supported_formats']['videos']
    
    def get_default_font(self, size):
        """Get a default font for the system."""
        try:
            # Try to use a common system font
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except OSError:
                try:
                    return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
                except OSError:
                    # Fall back to default font
                    return ImageFont.load_default()
    
    def add_watermark_to_image(self, input_path, output_path):
        """Add watermark to an image file."""
        try:
            # Open the image
            with Image.open(input_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create a transparent overlay
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                
                # Get watermark configuration
                watermark_config = self.config['watermark']
                text = watermark_config['text']
                font_size = watermark_config['font_size']
                # Use 70% opacity (179 = 70% of 255)
                font_color = tuple(watermark_config['font_color'] + [179])
                bg_color = watermark_config.get('background_color')
                padding = watermark_config['padding']
                margin = watermark_config['margin']
                
                # Get font
                font = self.get_default_font(font_size)
                
                # Calculate text size
                lines = text.split('\n')
                line_heights = []
                line_widths = []
                
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_widths.append(bbox[2] - bbox[0])
                    line_heights.append(bbox[3] - bbox[1])
                
                text_width = max(line_widths)
                text_height = sum(line_heights) + (len(lines) - 1) * 5  # 5px line spacing
                
                # Calculate watermark position (bottom-right)
                # Position text directly without background padding
                x = img.width - text_width - margin
                y = img.height - text_height - margin
                
                # Draw background rectangle only if background color is specified
                if bg_color is not None:
                    watermark_width = text_width + 2 * padding
                    watermark_height = text_height + 2 * padding
                    bg_x = img.width - watermark_width - margin
                    bg_y = img.height - watermark_height - margin
                    
                    draw.rectangle(
                        [bg_x, bg_y, bg_x + watermark_width, bg_y + watermark_height],
                        fill=tuple(bg_color)
                    )
                    # Adjust text position when background is present
                    x = bg_x + padding
                    y = bg_y + padding
                
                # Draw text lines
                current_y = y
                for i, line in enumerate(lines):
                    draw.text(
                        (x, current_y),
                        line,
                        fill=font_color,
                        font=font
                    )
                    current_y += line_heights[i] + 5
                
                # Composite the overlay onto the original image
                watermarked = Image.alpha_composite(img, overlay)
                
                # Convert back to RGB if original was not RGBA
                if Image.open(input_path).mode != 'RGBA':
                    watermarked = watermarked.convert('RGB')
                
                # Save the watermarked image
                watermarked.save(output_path, quality=95)
                logger.info(f"Successfully watermarked image: {input_path} -> {output_path}")
                
        except Exception as e:
            logger.error(f"Error watermarking image {input_path}: {e}")
            raise
    
    def escape_text_for_ffmpeg(self, text):
        """Properly escape text for FFmpeg drawtext filter."""
        # Replace newlines with literal \n for FFmpeg
        escaped_text = text.replace('\n', '\\n')
        
        # Escape colons which are parameter separators in FFmpeg
        escaped_text = escaped_text.replace(':', '\\:')
        
        # Escape other special characters that might cause issues
        escaped_text = escaped_text.replace("'", "\\'")
        escaped_text = escaped_text.replace('"', '\\"')
        escaped_text = escaped_text.replace('=', '\\=')
        escaped_text = escaped_text.replace('[', '\\[')
        escaped_text = escaped_text.replace(']', '\\]')
        
        return escaped_text
    
    def add_watermark_to_video(self, input_path, output_path):
        """Add watermark to a video file using FFmpeg."""
        try:
            # Prepare watermark text for FFmpeg
            watermark_config = self.config['watermark']
            raw_text = watermark_config['text']
            font_size = watermark_config['font_size']
            margin = watermark_config['margin']
            
            # Try multiple escape strategies for maximum compatibility
            escape_strategies = [
                {
                    'name': 'Standard escaping',
                    'text': self.escape_text_for_ffmpeg(raw_text)
                },
                {
                    'name': 'Simple escaping (fallback)',
                    'text': raw_text.replace('\n', '\\\\n').replace(':', '\\:')
                },
                {
                    'name': 'Basic replacement (last resort)',
                    'text': raw_text.replace('\n', ' | ').replace(':', ' ')
                }
            ]
            
            last_error = None
            for strategy in escape_strategies:
                try:
                    escaped_text = strategy['text']
                    logger.info(f"Trying watermark strategy: {strategy['name']}")
                    logger.debug(f"Escaped text: {repr(escaped_text)}")
                    
                    # Build FFmpeg command
                    # Use a more robust filter string construction
                    filter_parts = [
                        f"text={escaped_text}",
                        f"fontsize={font_size}",
                        "fontcolor=black@0.7",
                        f"x=w-tw-{margin}",
                        f"y=h-th-{margin}"
                    ]
                    filter_string = "drawtext=" + ":".join(filter_parts)
                    
                    cmd = [
                        'ffmpeg',
                        '-i', str(input_path),
                        '-vf', filter_string,
                        '-c:a', 'copy',  # Copy audio without re-encoding
                        '-y',  # Overwrite output file
                        str(output_path)
                    ]
                    
                    logger.debug(f"FFmpeg command: {' '.join(cmd)}")
                    
                    # Run FFmpeg
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Successfully watermarked video using {strategy['name']}: {input_path} -> {output_path}")
                        return
                    else:
                        last_error = result.stderr
                        logger.warning(f"Strategy '{strategy['name']}' failed: {result.stderr}")
                        continue
                        
                except subprocess.TimeoutExpired as e:
                    last_error = f"Timeout with strategy '{strategy['name']}'"
                    logger.warning(last_error)
                    continue
                except Exception as e:
                    last_error = f"Exception with strategy '{strategy['name']}': {e}"
                    logger.warning(last_error)
                    continue
            
            # If all strategies failed, raise the last error
            logger.error(f"All watermarking strategies failed. Last error: {last_error}")
            raise subprocess.CalledProcessError(1, "ffmpeg", last_error)
                
        except Exception as e:
            logger.error(f"Error watermarking video {input_path}: {e}")
            raise
    
    def process_file(self, input_path):
        """Process a single file by adding watermark."""
        input_path = Path(input_path)
        
        if not input_path.exists():
            logger.warning(f"File does not exist: {input_path}")
            return
        
        if not self.is_supported_file(input_path):
            logger.warning(f"Unsupported file format: {input_path}")
            return
        
        # Generate output path
        output_dir = Path(self.config['folders']['output'])
        output_path = output_dir / input_path.name
        
        # Avoid processing the same file multiple times
        if output_path.exists():
            logger.info(f"Output file already exists, skipping: {output_path}")
            return
        
        with self.processing_lock:
            try:
                logger.info(f"Processing file: {input_path}")
                
                if self.is_image_file(input_path):
                    self.add_watermark_to_image(input_path, output_path)
                elif self.is_video_file(input_path):
                    self.add_watermark_to_video(input_path, output_path)
                
                logger.info(f"File processed successfully: {output_path}")
                
            except Exception as e:
                logger.error(f"Failed to process file {input_path}: {e}")
                # Clean up partial output file if it exists
                if output_path.exists():
                    try:
                        output_path.unlink()
                    except:
                        pass
    
    def process_existing_files(self):
        """Process any existing files in the INPUT directory."""
        input_dir = Path(self.config['folders']['input'])
        
        for file_path in input_dir.iterdir():
            if file_path.is_file() and self.is_supported_file(file_path):
                self.process_file(file_path)

class FileWatcher(FileSystemEventHandler):
    """Handles file system events for the INPUT directory."""
    
    def __init__(self, processor):
        self.processor = processor
        super().__init__()
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            # Wait a moment for file to be fully written
            time.sleep(1)
            self.processor.process_file(event.src_path)
    
    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            # Wait a moment for file to be fully written
            time.sleep(1)
            self.processor.process_file(event.dest_path)

def check_ffmpeg():
    """Check if FFmpeg is available for video processing."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Main application entry point."""
    print("=== Watermark Application ===")
    print("Automatically adds watermarks to photos and videos")
    print("Place files in the INPUT folder to process them")
    print("Press Ctrl+C to stop\n")
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        logger.warning("FFmpeg not found. Video processing will not be available.")
        logger.warning("Please install FFmpeg for video watermarking support.")
    
    try:
        # Initialize processor
        processor = WatermarkProcessor()
        
        # Process any existing files
        logger.info("Processing existing files in INPUT directory...")
        processor.process_existing_files()
        
        # Set up file watcher
        event_handler = FileWatcher(processor)
        observer = Observer()
        observer.schedule(
            event_handler,
            path=processor.config['folders']['input'],
            recursive=False
        )
        
        # Start monitoring
        observer.start()
        logger.info("File monitoring started. Waiting for new files...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping application...")
            observer.stop()
        
        observer.join()
        logger.info("Application stopped.")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()