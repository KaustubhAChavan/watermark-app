#!/usr/bin/env python3
"""
Test the improved FFmpeg implementation with better error handling and escaping.
"""

import sys
import os
sys.path.append('/home/runner/work/watermark-app/watermark-app')

from app import WatermarkProcessor
import tempfile
import subprocess
from pathlib import Path

def create_test_video():
    """Create a simple test video."""
    temp_dir = Path("/tmp/watermark_test")
    temp_dir.mkdir(exist_ok=True)
    
    input_video = temp_dir / "test_input.mp4"
    
    print("Creating test video...")
    create_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=3:size=320x240:rate=1',
        '-y', str(input_video)
    ]
    
    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Failed to create test video: {result.stderr}")
            return None
        return input_video
    except Exception as e:
        print(f"Error creating test video: {e}")
        return None

def test_improved_watermarking():
    """Test the improved watermarking implementation."""
    print("=== Testing Improved FFmpeg Watermarking ===")
    
    # Create test video
    input_video = create_test_video()
    if not input_video:
        print("Failed to create test video")
        return False
    
    temp_dir = input_video.parent
    output_video = temp_dir / "watermarked_output.mp4"
    
    try:
        # Initialize the watermark processor
        processor = WatermarkProcessor('/home/runner/work/watermark-app/watermark-app/config.json')
        
        # Test the improved video watermarking
        print("\nTesting improved video watermarking...")
        processor.add_watermark_to_video(input_video, output_video)
        
        # Check if output was created successfully
        if output_video.exists() and output_video.stat().st_size > 0:
            print(f"✓ SUCCESS: Watermarked video created ({output_video.stat().st_size} bytes)")
            
            # Try to get video info to verify it's valid
            info_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(output_video)]
            try:
                result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✓ Output video is valid")
                else:
                    print("⚠️ Output video might be corrupted")
            except Exception:
                print("? Could not verify video validity")
                
            return True
        else:
            print("✗ FAILED: No output file created or file is empty")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: Exception during watermarking: {e}")
        return False
    finally:
        # Clean up
        for file in [input_video, output_video]:
            if file.exists():
                file.unlink()

def test_text_escaping():
    """Test the text escaping function specifically."""
    print("\n=== Testing Text Escaping Function ===")
    
    processor = WatermarkProcessor('/home/runner/work/watermark-app/watermark-app/config.json')
    
    test_texts = [
        "Armstrong Properties\nRavindra Bhubal\ncontact: 7387457889",
        "Simple text",
        "Text with: colons and = equals",
        "Text with [brackets] and 'quotes'",
        'Text with "double quotes" and special chars',
    ]
    
    for text in test_texts:
        escaped = processor.escape_text_for_ffmpeg(text)
        print(f"Original: {repr(text)}")
        print(f"Escaped:  {repr(escaped)}")
        print()

if __name__ == "__main__":
    test_text_escaping()
    success = test_improved_watermarking()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
    
    sys.exit(0 if success else 1)