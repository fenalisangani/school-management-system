"""Resize a photo to common phone lock screen portrait sizes."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance

OUT_DIR = Path(
    r"C:\Users\fenal\.cursor\projects\c-Users-fenal-Projects-school-management-system\assets"
)
DEFAULT_SRC = OUT_DIR / "edited-river-portrait.png"

SIZES = {
    "1080x1920": (1080, 1920),
    "1179x2556": (1179, 2556),
    "1290x2796": (1290, 2796),
}


def make_lockscreen(
    img: Image.Image,
    target_w: int,
    target_h: int,
    *,
    horizontal_bias: float = 0.58,
    vertical_bias: float = 0.42,
) -> Image.Image:
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    nw, nh = int(w * scale + 0.5), int(h * scale + 0.5)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    left = int((nw - target_w) * horizontal_bias)
    top = int((nh - target_h) * vertical_bias)
    left = max(0, min(left, nw - target_w))
    top = max(0, min(top, nh - target_h))

    cropped = resized.crop((left, top, left + target_w, top + target_h))
    cropped = ImageEnhance.Contrast(cropped).enhance(1.03)
    cropped = ImageEnhance.Color(cropped).enhance(1.02)
    return cropped


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    prefix = sys.argv[2] if len(sys.argv) > 2 else "lockscreen-river-portrait"
    horizontal_bias = float(sys.argv[3]) if len(sys.argv) > 3 else 0.58

    img = Image.open(src).convert("RGB")
    for label, (tw, th) in SIZES.items():
        out = make_lockscreen(img, tw, th, horizontal_bias=horizontal_bias)
        path = OUT_DIR / f"{prefix}-{label}.png"
        out.save(path, format="PNG", optimize=True)
        print(f"Saved {path.name}: {out.size}")

    main_path = OUT_DIR / f"{prefix}.png"
    best = make_lockscreen(img, 1290, 2796, horizontal_bias=horizontal_bias)
    best.save(main_path, format="PNG", optimize=True)
    print(f"Saved {main_path.name}: {best.size}")


if __name__ == "__main__":
    main()
