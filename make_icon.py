# -*- coding: utf-8 -*-
"""用鲸鱼娘头像生成应用图标 assets/icon.ico / icon.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BASE = Path(__file__).parent
SRC = BASE / "assets" / "pet" / "idle.png"
OUT_ICO = BASE / "assets" / "icon.ico"
OUT_PNG = BASE / "assets" / "icon.png"

SIZE = 512


def rounded_avatar(size: int) -> Image.Image:
    """蓝紫渐变圆底 + 角色头像。"""
    src = Image.open(SRC).convert("RGBA")
    head = src.crop((0, 0, src.width, int(src.height * 0.62)))

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # 渐变底
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        r = int(120 + (72 - 120) * t)
        g = int(160 + (110 - 160) * t)
        b = int(255 + (238 - 255) * t)
        gd.line([(0, y), (size, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    canvas.paste(grad, (0, 0), mask)

    # 角色：按宽度贴合，底部对齐
    scale = size / head.width * 0.96
    hw, hh = int(head.width * scale), int(head.height * scale)
    head = head.resize((hw, hh), Image.LANCZOS)
    canvas.alpha_composite(head, (int((size - hw) / 2), int(size - hh + size * 0.04)))

    # 再裁回圆形
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)

    # 柔和高光
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        (-size * 0.25, -size * 0.55, size * 0.75, size * 0.25), fill=(255, 255, 255, 60)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.05))
    out.alpha_composite(Image.composite(glow, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask))
    return out


def main() -> None:
    avatar = rounded_avatar(SIZE)
    avatar.save(OUT_PNG)
    avatar.save(
        OUT_ICO,
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print("saved", OUT_ICO, OUT_PNG)


if __name__ == "__main__":
    main()
