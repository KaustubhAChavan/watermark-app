#!/usr/bin/env python3
"""
Demo script for the watermark application.
Creates sample images, videos, and audio files to demonstrate the watermarking functionality.
"""

import os
from PIL import Image, ImageDraw

def create_demo_images():
    """Create sample images for demonstration."""
    print("Creating demo images...")
    
    # Create input_images directory if it doesn't exist
    os.makedirs('input_images', exist_ok=True)
    
    # Demo image 1: Business photo
    img1 = Image.new('RGB', (800, 600), color='skyblue')
    draw1 = ImageDraw.Draw(img1)
    draw1.text((50, 50), 'Sample Business Photo', fill='navy')
    draw1.rectangle([100, 150, 700, 450], outline='darkblue', width=5)
    draw1.text((300, 280), 'Property Image', fill='white')
    img1.save('input_images/business_photo.jpg')
    
    # Demo image 2: Property listing
    img2 = Image.new('RGB', (1024, 768), color='lightgreen')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((50, 50), 'Property Listing Photo', fill='darkgreen')
    draw2.ellipse([200, 200, 824, 568], outline='darkgreen', width=8)
    draw2.text((400, 350), 'FOR SALE', fill='red')
    img2.save('input_images/property_listing.png')
    
    # Demo image 3: Real estate photo
    img3 = Image.new('RGB', (600, 400), color='lightcoral')
    draw3 = ImageDraw.Draw(img3)
    draw3.text((50, 50), 'Real Estate Photo', fill='darkred')
    draw3.polygon([(100, 150), (500, 150), (300, 300)], outline='maroon', width=6)
    draw3.text((200, 200), 'HOME', fill='white')
    img3.save('input_images/real_estate.gif')
    
    print("Demo images created in input_images/ folder:")
    print("  - business_photo.jpg")
    print("  - property_listing.png") 
    print("  - real_estate.gif")

def create_demo_videos():
    """Create sample videos for demonstration (requires FFmpeg)."""
    print("Creating demo videos...")
    
    # Create input_videos directory if it doesn't exist
    os.makedirs('input_videos', exist_ok=True)
    
    try:
        import subprocess
        
        # Create a simple test video with color bars
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'testsrc=duration=10:size=640x480:rate=30',
            '-c:v', 'libx264',
            '-y',
            'input_videos/sample_video.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Demo video created: input_videos/sample_video.mp4")
        else:
            print("Could not create demo video (FFmpeg not available or failed)")
            
    except Exception as e:
        print(f"Could not create demo video: {e}")

def create_demo_audio():
    """Create sample audio files for demonstration (requires FFmpeg)."""
    print("Creating demo audio...")
    
    # Create input_audio directory if it doesn't exist
    os.makedirs('input_audio', exist_ok=True)
    
    try:
        import subprocess
        
        # Create a simple test audio file with sine wave
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=5',
            '-c:a', 'aac',
            '-y',
            'input_audio/sample_audio.aac'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Demo audio created: input_audio/sample_audio.aac")
        else:
            print("Could not create demo audio (FFmpeg not available or failed)")
            
    except Exception as e:
        print(f"Could not create demo audio: {e}")

if __name__ == "__main__":
    create_demo_images()
    create_demo_videos()
    create_demo_audio()
    print("\nDemo files created! Run 'python app.py' to process them!")
    print("\nFolder structure:")
    print("  input_images/  - Place images here")
    print("  input_videos/  - Place videos here") 
    print("  input_audio/   - Place audio files here")
    print("  output_images/ - Watermarked images will appear here")
    print("  output_videos/ - Watermarked videos will appear here")