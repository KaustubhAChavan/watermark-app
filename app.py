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
        """Create input and output directories for images, videos, and audio if they don't exist."""
        folders = self.config['folders']
        
        # Create all required directories
        for folder_key, folder_path in folders.items():
            dir_path = Path(folder_path)
            dir_path.mkdir(exist_ok=True)
            logger.info(f"{folder_key} directory: {dir_path.absolute()}")
        
        # Store paths for easy access
        self.input_images_dir = Path(folders['input_images'])
        self.output_images_dir = Path(folders['output_images'])
        self.input_videos_dir = Path(folders['input_videos'])
        self.output_videos_dir = Path(folders['output_videos'])
        self.input_audio_dir = Path(folders['input_audio'])
    
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
    
    def is_audio_file(self, file_path):
        """Check if file is a supported audio format."""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.config['supported_formats']['audio']
    
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
                font_color = tuple(watermark_config['font_color'] + [255])  # Add alpha
                bg_color = tuple(watermark_config['background_color'])
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
                
                # Calculate watermark position (center)
                watermark_width = text_width + 2 * padding
                watermark_height = text_height + 2 * padding
                
                x = (img.width - watermark_width) // 2
                y = (img.height - watermark_height) // 2
                
                # Draw background rectangle
                draw.rectangle(
                    [x, y, x + watermark_width, y + watermark_height],
                    fill=bg_color
                )
                
                # Draw text lines
                current_y = y + padding
                for i, line in enumerate(lines):
                    draw.text(
                        (x + padding, current_y),
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
    
    def find_matching_audio(self, video_path):
        """Find a matching audio file for the video."""
        video_stem = Path(video_path).stem
        
        # Look for audio files with the same name
        for audio_file in self.input_audio_dir.iterdir():
            if audio_file.is_file() and self.is_audio_file(audio_file):
                if audio_file.stem == video_stem:
                    return audio_file
        
        # If no exact match, return the first available audio file
        for audio_file in self.input_audio_dir.iterdir():
            if audio_file.is_file() and self.is_audio_file(audio_file):
                return audio_file
        
        return None
    
    def get_video_duration(self, video_path):
        """Get video duration in seconds using FFmpeg."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                return float(data['format']['duration'])
        except Exception as e:
            logger.warning(f"Could not get video duration: {e}")
        return None
    
    def add_watermark_to_video(self, input_path, output_path):
        """Add moving watermark to a video file and replace audio."""
        try:
            # Prepare watermark text for FFmpeg
            watermark_config = self.config['watermark']
            raw_text = watermark_config['text']
            font_size = watermark_config['font_size']
            
            # Find matching audio file
            audio_file = self.find_matching_audio(input_path)
            
            # Get video duration for audio looping
            video_duration = self.get_video_duration(input_path)
            
            # Escape text for FFmpeg
            escaped_text = self.escape_text_for_ffmpeg(raw_text)
            
            # Create moving watermark filter - from center top to bottom
            # y moves from top (margin) to bottom (h - text_height - margin) throughout the video
            # Using a simple linear interpolation over time
            filter_parts = [
                f"text={escaped_text}",
                f"fontsize={font_size}",
                "fontcolor=white@0.8",
                "x=(w-text_w)/2",  # Center horizontally
                "y=30+(h-text_h-60)*t/duration",  # Move from top to bottom over video duration
                "box=1",
                "boxcolor=black@0.5",
                "boxborderw=10"
            ]
            
            # Build FFmpeg command
            cmd = ['ffmpeg', '-i', str(input_path)]
            
            # Add audio processing if audio file exists
            if audio_file and video_duration:
                logger.info(f"Adding audio from: {audio_file}")
                
                # Create looped audio to match video duration
                cmd.extend(['-i', str(audio_file)])
                
                # Complex filter for audio looping and video watermarking
                video_filter = "drawtext=" + ":".join(filter_parts)
                audio_filter = f"aloop=loop=-1:size=2e+09,atrim=duration={video_duration}"
                
                cmd.extend([
                    '-filter_complex', f"[1:a]{audio_filter}[looped_audio];[0:v]{video_filter}[watermarked_video]",
                    '-map', '[watermarked_video]',
                    '-map', '[looped_audio]',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-shortest'  # Stop when shortest stream ends
                ])
            else:
                # Video only with moving watermark
                video_filter = "drawtext=" + ":".join(filter_parts)
                cmd.extend([
                    '-vf', video_filter,
                    '-c:a', 'copy'  # Copy original audio if no replacement
                ])
            
            cmd.extend(['-y', str(output_path)])  # Overwrite output file
            
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for video processing
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully watermarked video: {input_path} -> {output_path}")
                if audio_file:
                    logger.info(f"Audio added from: {audio_file}")
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, "ffmpeg", result.stderr)
                
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
        
        # Determine output path based on file type
        if self.is_image_file(input_path):
            output_path = self.output_images_dir / input_path.name
        elif self.is_video_file(input_path):
            output_path = self.output_videos_dir / input_path.name
        else:
            logger.warning(f"Unknown file type: {input_path}")
            return
        
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
        """Process any existing files in the input directories."""
        # Process images
        for file_path in self.input_images_dir.iterdir():
            if file_path.is_file() and self.is_image_file(file_path):
                self.process_file(file_path)
        
        # Process videos  
        for file_path in self.input_videos_dir.iterdir():
            if file_path.is_file() and self.is_video_file(file_path):
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
        
        # Set up file watchers for both input directories
        event_handler = FileWatcher(processor)
        observer = Observer()
        
        # Watch images directory
        observer.schedule(
            event_handler,
            path=str(processor.input_images_dir),
            recursive=False
        )
        
        # Watch videos directory  
        observer.schedule(
            event_handler,
            path=str(processor.input_videos_dir),
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