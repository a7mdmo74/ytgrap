"""Generate branded YTGrab icons for the browser extension using Pillow."""
import os
from PIL import Image, ImageDraw, ImageFont


def create_icon(size):
    """Create a YTGrab branded icon: dark circle with amber border and 'YT' text."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2
    radius = size / 2 - 0.5
    border = max(1, int(size * 0.08))

    # Amber border circle
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(226, 183, 20, 255)
    )

    # Dark inner circle
    inner = radius - border
    draw.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        fill=(22, 33, 62, 255)
    )

    # Draw "YT" text
    text = "YT"
    font_size = int(size * 0.45)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw / 2
    ty = cy - th / 2 - bbox[1]

    draw.text((tx, ty), text, fill=(226, 183, 20, 255), font=font)

    return img


def main():
    icons_dir = os.path.join(os.path.dirname(__file__), 'browser_extension', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    for size in [16, 48, 128]:
        img = create_icon(size)
        filepath = os.path.join(icons_dir, f'icon{size}.png')
        img.save(filepath, 'PNG')
        print(f"Created {filepath} ({size}x{size})")


if __name__ == '__main__':
    main()
