#!/usr/bin/env python3
"""
Test script to reproduce the FFmpeg command syntax error.
"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_ffmpeg_command():
    """Test the current FFmpeg command that has the syntax error."""
    
    # Create a simple test video using FFmpeg
    temp_dir = Path("/tmp/ffmpeg_test")
    temp_dir.mkdir(exist_ok=True)
    
    input_video = temp_dir / "test_input.mp4"
    output_video = temp_dir / "test_output.mp4"
    
    print("Creating test video...")
    # Create a simple 5-second test video with color bars
    create_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=1',
        '-y', str(input_video)
    ]
    
    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Failed to create test video: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("Timeout creating test video")
        return False
    except FileNotFoundError:
        print("FFmpeg not found! Please install FFmpeg to test video processing.")
        return False
    
    print(f"Test video created: {input_video}")
    
    # Now test the problematic watermark command
    print("\nTesting problematic FFmpeg command...")
    
    # Let me test the exact problematic string from the error message
    # The error shows: "No option name near ' 7387457889:fontsize=24..."
    # This suggests the colon in the phone number is causing the issue
    
    # Test with the exact text from config.json
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    original_text = config['watermark']['text']
    watermark_text = original_text.replace('\n', '\\n')
    font_size = 24
    margin = 30
    
    print(f"Original text: {repr(original_text)}")
    print(f"Processed text: {repr(watermark_text)}")
    
    # The problematic command from app.py
    cmd = [
        'ffmpeg',
        '-i', str(input_video),
        '-vf', f"drawtext=text='{watermark_text}':fontsize={font_size}:fontcolor=white@0.8:x=w-tw-{margin}:y=h-th-{margin}:box=1:boxcolor=black@0.5:boxborderw=10",
        '-c:a', 'copy',
        '-y', str(output_video)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Filter string: {cmd[4]}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✓ FFmpeg command succeeded (unexpected!)")
            return True
        else:
            print("✗ FFmpeg command failed as expected:")
            print(f"Error: {result.stderr}")
            
            # Check if it's the specific error we're looking for
            if "No option name near" in result.stderr and "7387457889" in result.stderr:
                print("✓ Confirmed: This is the exact error mentioned in the issue!")
                return True
            else:
                print("? Different error than expected")
                return False
                
    except subprocess.TimeoutExpired:
        print("✗ Timeout running FFmpeg command")
        return False
    
    finally:
        # Clean up
        for file in [input_video, output_video]:
            if file.exists():
                file.unlink()

if __name__ == "__main__":
    print("=== FFmpeg Command Syntax Error Test ===")
    test_ffmpeg_command()