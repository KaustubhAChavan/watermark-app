#!/usr/bin/env python3
"""
Test edge cases and simulate potential Windows-specific FFmpeg issues.
"""

import subprocess
import tempfile
from pathlib import Path

def test_windows_command_simulation():
    """Simulate the type of command that might fail on Windows."""
    print("=== Testing Windows-style Command Scenarios ===")
    
    temp_dir = Path("/tmp/windows_test")
    temp_dir.mkdir(exist_ok=True)
    
    input_video = temp_dir / "test_input.mp4"
    output_video = temp_dir / "test_output.mp4"
    
    # Create test video
    create_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=2:size=320x240:rate=1',
        '-y', str(input_video)
    ]
    
    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Failed to create test video: {result.stderr}")
            return
    except Exception as e:
        print(f"Error creating test video: {e}")
        return
    
    # Test scenarios that might cause issues on Windows
    test_scenarios = [
        {
            "name": "Unescaped colon (problematic)",
            "text": "Armstrong Properties\\nRavindra Bhubal\\ncontact: 7387457889",
            "should_work": True  # Works on modern FFmpeg but might fail on older versions/Windows
        },
        {
            "name": "Properly escaped colon",
            "text": "Armstrong Properties\\nRavindra Bhubal\\ncontact\\: 7387457889", 
            "should_work": True
        },
        {
            "name": "Multiple special characters",
            "text": "Company\\: Test\\nName\\: John\\nPhone\\: 123\\:456\\:7890",
            "should_work": True
        },
        {
            "name": "Complex escaping test",
            "text": "Text with \\[brackets\\] and \\= equals and \\: colons",
            "should_work": True
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i+1}: {scenario['name']} ---")
        
        output_file = temp_dir / f"output_{i+1}.mp4"
        
        # Create the filter string as the app would
        filter_string = f"drawtext=text='{scenario['text']}':fontsize=24:fontcolor=white@0.8:x=w-tw-30:y=h-th-30:box=1:boxcolor=black@0.5:boxborderw=10"
        
        cmd = [
            'ffmpeg',
            '-i', str(input_video),
            '-vf', filter_string,
            '-c:a', 'copy',
            '-y', str(output_file)
        ]
        
        print(f"Text: {repr(scenario['text'])}")
        print(f"Filter: {filter_string}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✓ SUCCESS")
            else:
                print("✗ FAILED")
                print(f"  Error: {result.stderr}")
                
                # Check for the specific syntax error from the issue
                if "No option name near" in result.stderr:
                    print("  ⚠️  This matches the reported syntax error pattern!")
                    
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")
        
        # Clean up
        if output_file.exists():
            output_file.unlink()
    
    # Clean up
    if input_video.exists():
        input_video.unlink()

def test_manual_bad_command():
    """Test a manually crafted command that should fail."""
    print("\n=== Testing Manually Bad Command ===")
    
    temp_dir = Path("/tmp/bad_test")
    temp_dir.mkdir(exist_ok=True)
    
    input_video = temp_dir / "test_input.mp4"
    output_video = temp_dir / "test_output.mp4"
    
    # Create test video
    create_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=160x120:rate=1',
        '-y', str(input_video)
    ]
    
    try:
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return
    except Exception:
        return
    
    # Create a command that will definitely fail due to syntax issues
    bad_commands = [
        {
            "name": "Broken parameter syntax",
            "filter": "drawtext=text=test:broken:syntax:fontsize=24"
        },
        {
            "name": "Invalid option name",
            "filter": "drawtext=text=test:invalidoption=value:fontsize=24"
        }
    ]
    
    for cmd_test in bad_commands:
        print(f"\nTesting: {cmd_test['name']}")
        
        cmd = [
            'ffmpeg', '-i', str(input_video), '-vf', cmd_test['filter'],
            '-y', str(output_video)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print("✓ Command failed as expected")
                print(f"  Error: {result.stderr[:200]}...")
            else:
                print("? Command unexpectedly succeeded")
        except Exception as e:
            print(f"Exception: {e}")
    
    # Clean up
    for file in [input_video, output_video]:
        if file.exists():
            file.unlink()

if __name__ == "__main__":
    test_windows_command_simulation()
    test_manual_bad_command()