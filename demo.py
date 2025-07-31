#!/usr/bin/env python3
"""
Demo script for the watermark application.
Creates sample images and videos to demonstrate the watermarking functionality.
"""

import os
from PIL import Image, ImageDraw

def create_demo_images():
    """Create sample images for demonstration."""
    print("Creating demo images...")
    
    # Create INPUT directory if it doesn't exist
    os.makedirs('INPUT', exist_ok=True)
    
    # Demo image 1: Business photo
    img1 = Image.new('RGB', (800, 600), color='skyblue')
    draw1 = ImageDraw.Draw(img1)
    draw1.text((50, 50), 'Sample Business Photo', fill='navy')
    draw1.rectangle([100, 150, 700, 450], outline='darkblue', width=5)
    draw1.text((300, 280), 'Property Image', fill='white')
    img1.save('INPUT/business_photo.jpg')
    
    # Demo image 2: Property listing
    img2 = Image.new('RGB', (1024, 768), color='lightgreen')
    draw2 = ImageDraw.Draw(img2)
    draw2.text((50, 50), 'Property Listing Photo', fill='darkgreen')
    draw2.ellipse([200, 200, 824, 568], outline='darkgreen', width=8)
    draw2.text((400, 350), 'FOR SALE', fill='red')
    img2.save('INPUT/property_listing.png')
    
    # Demo image 3: Real estate photo
    img3 = Image.new('RGB', (600, 400), color='lightcoral')
    draw3 = ImageDraw.Draw(img3)
    draw3.text((50, 50), 'Real Estate Photo', fill='darkred')
    draw3.polygon([(100, 150), (500, 150), (300, 300)], outline='maroon', width=6)
    draw3.text((200, 200), 'HOME', fill='white')
    img3.save('INPUT/real_estate.gif')
    
    print("Demo images created in INPUT/ folder:")
    print("  - business_photo.jpg")
    print("  - property_listing.png") 
    print("  - real_estate.gif")
    print("\nRun 'python app.py' to process these images!")

if __name__ == "__main__":
    create_demo_images()