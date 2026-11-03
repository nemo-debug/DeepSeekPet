# -*- coding: utf-8 -*-
"""处理 AI 生成的三帧鲸鱼娘素材：
1) 抠掉 AI 画上去的灰白棋盘格背景（掩膜 + 边缘连通填充）
2) 清掉右下角水印
3) 用三帧并集 bbox 统一裁剪（保证切帧不跳动）
4) 统一缩放到指定高度，输出 assets/pet/{idle,blink,happy}.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

RAW = Path(__file__).parent / "assets" / "raw2"
OUT = Path(__file__).parent / "assets" / "pet"
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "idle": "Chibi_anime_whale_girl_maid_ch_2026-10-22T01-08-32.png",
    "blink": "Keep_this_exact_same_chibi_wha_2026-10-22T01-08-52.png",
    "happy": "Keep_this_exact_same_chibi_wha_2026-10-22T01-09-10.png",
}

TARGET_H = 620
SEED = 128  # 背景标记色


def strip_background(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    arr = np.array(im.convert("RGB")).astype(np.int16)
    mx = arr.max(axis=2)
    mn = arr.min(axis=2)
    sat = mx - mn
    bright = mx
    bg_like = (sat <= 22) & (bright >= 178)

    mask = Image.fromarray((bg_like * 255).astype(np.uint8), mode="L")
    w, h = mask.size

    # 只删与画布边缘连通的灰白区域（保护角色内部的白色围裙/高光）
    lbl, n = ndimage.label(bg_like)
    border = np.concatenate(
        [lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]
    )
    keep = set(int(v) for v in np.unique(border) if v != 0)
    bg = np.isin(lbl, list(keep))
    print(f"  mask={bg_like.mean():.1%} connected-bg={bg.mean():.1%} regions={n}")

    # 水印区域直接清空（右下角，角色主体不在该处）
    wx, wy = int(w * 0.84), int(h * 0.90)
    bg[wy:, wx:] = True

    alpha = np.array(im.getchannel("A"))
    alpha[bg] = 0

    # 收一圈，去掉贴着背景的抗锯齿灰边
    a_img = Image.fromarray(alpha, mode="L").filter(ImageFilter.MinFilter(3))
    # 轻微羽化让边缘不那么硬
    a_img = a_img.filter(ImageFilter.GaussianBlur(0.6))
    im.putalpha(a_img)
    return im


def main() -> None:
    frames = {}
    for key, name in FILES.items():
        im = Image.open(RAW / name)
        frames[key] = strip_background(im)
        print(key, "bg removed")

    boxes = [im.getbbox() for im in frames.values()]
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    pad = 10
    w, h = frames["idle"].size
    box = (max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad))
    print("union bbox:", box)

    for key, im in frames.items():
        crop = im.crop(box)
        ratio = TARGET_H / crop.height
        size = (max(1, round(crop.width * ratio)), TARGET_H)
        out = crop.resize(size, Image.LANCZOS)
        out.save(OUT / f"{key}.png")
        print(key, "->", size)

    # 预览：贴在深色/浅色背景上看效果
    sheet = Image.new("RGB", (1290, 700), (28, 32, 48))
    light = Image.new("RGB", (1290, 700), (243, 246, 252))
    for i, key in enumerate(("idle", "blink", "happy")):
        im = Image.open(OUT / f"{key}.png")
        sheet.paste(im, (20 + i * 420, 40), im)
        light.paste(im, (20 + i * 420, 40), im)
    sheet.save(Path(__file__).parent / "preview_dark.png")
    light.save(Path(__file__).parent / "preview_light.png")
    print("previews saved")


if __name__ == "__main__":
    main()
