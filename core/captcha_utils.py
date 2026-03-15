"""
DeepFake Shield — Strong Image CAPTCHA Generator
Generates distorted text images using Pillow.
No external API needed. CPU-friendly.
"""

import io
import os
import random
import string
import base64
import math
import logging

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not available for image CAPTCHA.")


def generate_captcha_text(length=5):
    """Generate random CAPTCHA text (avoiding confusing chars)."""
    # Remove confusing characters: 0/O, 1/l/I, 5/S, 2/Z
    chars = 'ABCDEFGHJKLMNPQRTUVWXY3467889'
    return ''.join(random.choices(chars, k=length))


def generate_math_captcha():
    """Fallback: generate math CAPTCHA if Pillow fails."""
    ops = [
        ('+', lambda a, b: a + b),
        ('-', lambda a, b: a - b),
        ('×', lambda a, b: a * b),
    ]
    op_symbol, op_func = random.choice(ops)

    if op_symbol == '×':
        a = random.randint(2, 9)
        b = random.randint(2, 9)
    elif op_symbol == '-':
        a = random.randint(10, 30)
        b = random.randint(1, a - 1)
    else:
        a = random.randint(5, 25)
        b = random.randint(3, 20)

    answer = str(op_func(a, b))
    question = f"{a} {op_symbol} {b} = ?"
    return question, answer, None


def generate_image_captcha(text=None, width=220, height=70):
    """
    Generate a distorted image CAPTCHA.
    Returns (captcha_text, base64_image_string).
    """
    if not PIL_AVAILABLE:
        q, a, _ = generate_math_captcha()
        return a, q, None

    if text is None:
        text = generate_captcha_text(5)

    # Create image
    img = Image.new('RGB', (width, height), color=_random_bg_color())
    draw = ImageDraw.Draw(img)

    # Try to load a font
    font = _get_font(32)

    # Draw noise lines
    for _ in range(random.randint(4, 8)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = _random_dark_color()
        line_width = random.randint(1, 2)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=line_width)

    # Draw noise dots
    for _ in range(random.randint(80, 150)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=_random_dark_color())

    # Draw each character with random rotation and position
    char_width = (width - 20) // len(text)
    x_offset = 10

    for i, char in enumerate(text):
        # Create character image for rotation
        char_img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)

        char_color = _random_text_color()
        char_font = _get_font(random.randint(26, 36))

        # Get text bounding box
        bbox = char_draw.textbbox((0, 0), char, font=char_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        char_draw.text(
            ((50 - tw) // 2, (50 - th) // 2 - 4),
            char,
            font=char_font,
            fill=char_color
        )

        # Random rotation
        angle = random.randint(-25, 25)
        char_img = char_img.rotate(angle, expand=False, resample=Image.BICUBIC)

        # Paste onto main image
        y_pos = random.randint(2, max(3, height - 48))
        img.paste(char_img, (x_offset, y_pos), char_img)
        x_offset += char_width

    # Draw more noise curves (sine wave)
    draw2 = ImageDraw.Draw(img)
    amp = random.randint(3, 6)
    period = random.randint(40, 80)
    y_base = height // 2 + random.randint(-10, 10)
    for x in range(0, width, 2):
        y = int(y_base + amp * math.sin(x * 2 * math.pi / period))
        draw2.ellipse(
            [x - 1, y - 1, x + 1, y + 1],
            fill=_random_dark_color()
        )

    # Apply slight blur
    img = img.filter(ImageFilter.SMOOTH)

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return text, f"data:image/png;base64,{img_base64}", img_base64


def _random_bg_color():
    """Light background color."""
    return (
        random.randint(210, 245),
        random.randint(215, 245),
        random.randint(220, 250),
    )


def _random_text_color():
    """Dark text color."""
    return (
        random.randint(10, 80),
        random.randint(10, 80),
        random.randint(30, 100),
    )


def _random_dark_color():
    """Random dark-ish color for noise."""
    return (
        random.randint(60, 160),
        random.randint(60, 160),
        random.randint(60, 160),
    )


def _get_font(size):
    """Try to load a suitable font, fallback to default."""
    font_paths = [
        # Windows
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/verdana.ttf',
        'C:/Windows/Fonts/cour.ttf',
        'C:/Windows/Fonts/consola.ttf',
        # Linux
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
        # Mac
        '/Library/Fonts/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                from PIL import ImageFont
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    try:
        from PIL import ImageFont
        return ImageFont.load_default()
    except Exception:
        return None