"""Run this to create extension icons."""
from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('icons', exist_ok=True)

for size in [16, 48, 128]:
    img = Image.new('RGBA', (size, size), (102, 126, 234, 255))
    draw = ImageDraw.Draw(img)
    # Draw a shield shape
    cx, cy = size // 2, size // 2
    r = size // 2 - 2
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(102, 126, 234, 255))
    # Draw checkmark
    s = size // 4
    draw.text((cx-s//2, cy-s//2), "✓", fill='white')
    img.save(f'icons/icon{size}.png')
    print(f"Created icon{size}.png")