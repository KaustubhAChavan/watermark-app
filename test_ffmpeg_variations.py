#!/usr/bin/env python3
"""
Test different FFmpeg command variations to understand the syntax issue.
"""

import subprocess
import tempfile
import os
from pathlib import Path

def create_test_video():
    """Create a simple test video."""
    temp_dir = Path("/tmp/ffmpeg_test")
    temp_dir.mkdir(exist_ok=True)
    
    input_video = temp_dir / "test_input.mp4"
    
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
            return None
        return input_video
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Error creating test video: {e}")
        return None

def test_ffmpeg_variations(input_video):
    """Test different FFmpeg command variations."""
    temp_dir = input_video.parent
    
    # Test data - the problematic text
    original_text = "Armstrong Properties\nRavindra Bhubal\ncontact: 7387457889"
    
    test_cases = [
        {
            "name": "Current implementation (single quotes)",
            "text": original_text.replace('\n', '\\n'),
            "filter": lambda text: f"drawtext=text='{text}':fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10"
        },
        {
            "name": "No quotes around text",
            "text": original_text.replace('\n', '\\n'),
            "filter": lambda text: f"drawtext=text={text}:fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10"
        },
        {
            "name": "Escape colons in text",
            "text": original_text.replace('\n', '\\n').replace(':', '\\:'),
            "filter": lambda text: f"drawtext=text='{text}':fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10"
        },
        {
            "name": "Double quotes instead of single",
            "text": original_text.replace('\n', '\\n'),
            "filter": lambda text: f'drawtext=text="{text}":fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10'
        },
        {
            "name": "Escape colons + double quotes",
            "text": original_text.replace('\n', '\\n').replace(':', '\\:'),
            "filter": lambda text: f'drawtext=text="{text}":fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10'
        },
        {
            "name": "Windows-style escaping simulation",
            "text": original_text.replace('\n', '\\\\n').replace(':', '\\:'),
            "filter": lambda text: f"drawtext=text='{text}':fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test {i+1}: {test_case['name']} ---")
        
        output_video = temp_dir / f"test_output_{i+1}.mp4"
        
        filter_string = test_case['filter'](test_case['text'])
        print(f"Text: {repr(test_case['text'])}")
        print(f"Filter: {filter_string}")
        
        cmd = [
            'ffmpeg',
            '-i', str(input_video),
            '-vf', filter_string,
            '-c:a', 'copy',
            '-y', str(output_video)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✓ SUCCESS")
                # Check if output file was created and has size
                if output_video.exists() and output_video.stat().st_size > 0:
                    print(f"  Output file created: {output_video.stat().st_size} bytes")
                else:
                    print("  Warning: Output file is empty or missing")
            else:
                print("✗ FAILED")
                print(f"  Error: {result.stderr}")
                
                # Check for the specific error mentioned in the issue
                if "No option name near" in result.stderr and "7387457889" in result.stderr:
                    print("  ⚠️  This matches the reported error!")
                
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
        
        # Clean up output file
        if output_video.exists():
            output_video.unlink()

if __name__ == "__main__":
    print("=== FFmpeg Command Variations Test ===")
    
    input_video = create_test_video()
    if input_video:
        test_ffmpeg_variations(input_video)
        
        # Clean up
        if input_video.exists():
            input_video.unlink()
    else:
        print("Failed to create test video")