from PIL import Image, ImageDraw
import os

for size in [192, 512]:
    img = Image.new('RGBA', (size, size), (10, 14, 26, 255))
    draw = ImageDraw.Draw(img)
    # Shield circle
    cx, cy = size//2, size//2
    r = size//3
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(102, 126, 234, 255))
    # Inner circle
    r2 = r - size//10
    draw.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(10, 14, 26, 255))
    # Checkmark
    r3 = r2 - size//15
    draw.ellipse([cx-r3, cy-r3, cx+r3, cy+r3], fill=(102, 126, 234, 255))
    img.save(f'icon-{size}.png')
    print(f'Created icon-{size}.png')