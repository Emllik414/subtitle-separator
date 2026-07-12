from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


SIZE = 1024


def _lerp(a: int, b: int, t: float) -> int:
    return round(a * (1 - t) + b * t)


def build_icon(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (90, 110, SIZE - 90, SIZE - 70),
        radius=220,
        fill=(0, 0, 0, 90),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(35)))

    background = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = background.load()
    top = (10, 132, 255)
    bottom = (83, 92, 255)
    for y in range(80, SIZE - 80):
        t = (y - 80) / (SIZE - 161)
        color = (
            _lerp(top[0], bottom[0], t),
            _lerp(top[1], bottom[1], t),
            _lerp(top[2], bottom[2], t),
            255,
        )
        for x in range(80, SIZE - 80):
            pixels[x, y] = color

    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (80, 80, SIZE - 80, SIZE - 80), radius=210, fill=255
    )
    background.putalpha(mask)
    image.alpha_composite(background)

    card_shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(card_shadow).rounded_rectangle(
        (190, 263, 834, 773), radius=105, fill=(0, 0, 0, 55)
    )
    image.alpha_composite(card_shadow.filter(ImageFilter.GaussianBlur(24)))

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((190, 245, 834, 755), radius=105, fill=(255, 255, 255, 242))
    draw.rounded_rectangle((258, 340, 766, 440), radius=44, fill=(240, 247, 255, 255))
    draw.rounded_rectangle((258, 560, 766, 660), radius=44, fill=(240, 247, 255, 255))

    draw.rounded_rectangle((315, 373, 470, 407), radius=17, fill=(20, 100, 220, 255))
    draw.rounded_rectangle((510, 373, 708, 407), radius=17, fill=(40, 121, 230, 235))
    draw.rounded_rectangle((315, 593, 510, 627), radius=17, fill=(88, 100, 255, 235))
    draw.rounded_rectangle((550, 593, 708, 627), radius=17, fill=(88, 100, 255, 255))

    split = (60, 73, 210, 255)
    draw.rounded_rectangle((494, 445, 530, 535), radius=18, fill=split)
    draw.line(((512, 508), (430, 555)), fill=split, width=34)
    draw.line(((512, 508), (594, 555)), fill=split, width=34)
    draw.polygon(((413, 553), (454, 530), (451, 575)), fill=split)
    draw.polygon(((611, 553), (570, 530), (573, 575)), fill=split)

    png_path = output_dir / "app_icon.png"
    ico_path = output_dir / "app_icon.ico"
    image.save(png_path)
    image.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    return png_path, ico_path


if __name__ == "__main__":
    png, ico = build_icon(Path("assets"))
    print(f"Created {png}")
    print(f"Created {ico}")
