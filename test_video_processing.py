#!/usr/bin/env python3
"""
Quick test to process the video file directly using the improved implementation.
"""

import sys
sys.path.append('/home/runner/work/watermark-app/watermark-app')

from app import WatermarkProcessor
from pathlib import Path

def test_video_processing():
    """Test video processing with the new implementation."""
    print("=== Testing Video Processing ===")
    
    processor = WatermarkProcessor('/home/runner/work/watermark-app/watermark-app/config.json')
    
    input_path = Path('/home/runner/work/watermark-app/watermark-app/INPUT/test_video.mp4')
    output_path = Path('/home/runner/work/watermark-app/watermark-app/OUTPUT/test_video.mp4')
    
    if not input_path.exists():
        print(f"Input video not found: {input_path}")
        return False
    
    try:
        print(f"Processing video: {input_path}")
        processor.add_watermark_to_video(input_path, output_path)
        
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"✓ SUCCESS: Video processed successfully ({output_path.stat().st_size} bytes)")
            return True
        else:
            print("✗ FAILED: Output video not created or empty")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: Exception during processing: {e}")
        return False

if __name__ == "__main__":
    success = test_video_processing()
    print(f"\nVideo processing test: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)