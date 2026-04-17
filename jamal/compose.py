from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PADDING = 20
BACKGROUND = (15, 15, 30)


def compose(png_paths: list[Path], output_path: Path, title: str = "") -> None:
    images = [Image.open(p).convert("RGB") for p in png_paths]

    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images) + PADDING * (len(images) + 1)
    header_height = 60 if title else 0

    canvas = Image.new("RGB", (max_width + PADDING * 2, total_height + header_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    if title:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            ((max_width + PADDING * 2 - text_w) // 2, 16),
            title,
            fill=(200, 200, 220),
            font=font,
        )

    y_offset = header_height + PADDING
    for img in images:
        x_offset = (max_width - img.width) // 2 + PADDING
        canvas.paste(img, (x_offset, y_offset))
        y_offset += img.height + PADDING

    canvas.save(output_path, format="PNG", optimize=True)
