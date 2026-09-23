#!/usr/bin/env python3
"""Resize and compress raster assets for static hosting (WebP, alpha preserved)."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Lossy WebP — strong quality without going lossless (quality 90).
WEBP_QUALITY = 90

# Max dimension (fits inside square). Sized so bitmaps stay crisp under heavy browser zoom
# (e.g. 400%) — roughly “retina” × zoom headroom vs the on-screen CSS size.
RULES = {
    # Phone screenshots (.project-screenshot): narrow column tiles; need lots of pixels for zoom.
    "screenshot": (
        {"tummy-1.png", "tummy-2.png", "tummy-3.png",
         "photo-1.png", "photo-2.png", "photo-3.png",
         "latex-1.png", "latex-2.png", "latex-3.png",
         "falling-1.png", "falling-2.png", "falling-3.png"},
        (2400, 2400),
    ),
    # Hero cards (.for-fun-single-image): ~450×280 CSS — high cap preserves source detail.
    "hero": (
        {"creator-sub.png", "watch-0.png"},
        (1800, 1800),
    ),
    # Inline logos (~1.6em) — still tiny on screen but sharp when zoomed.
    "logo": (
        {"snapchat-logo.png", "datadog-logo.png", "teladoc-logo.png"},
        (768, 384),
    ),
}


def thumbnail_to_box(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    """RGBA image scaled to fit inside box; returns new Image."""
    out = im.copy()
    out.thumbnail(box, Image.Resampling.LANCZOS)
    return out


def main() -> None:
    name_to_rule: dict[str, tuple[str, tuple[int, int]]] = {}
    for kind, (names, box) in RULES.items():
        for name in names:
            name_to_rule[name] = (kind, box)

    for png_name in sorted(name_to_rule.keys()):
        src = ROOT / png_name
        if not src.exists():
            raise SystemExit(f"missing {src}")

        kind, box = name_to_rule[png_name]
        im = Image.open(src).convert("RGBA")
        resized = thumbnail_to_box(im, box)
        stem = png_name.replace(".png", "")
        dst = ROOT / f"{stem}.webp"
        resized.save(
            dst,
            format="WEBP",
            quality=WEBP_QUALITY,
            method=6,
            lossless=False,
        )
        print(f"{png_name} → {dst.name} ({kind}, box={box})")


if __name__ == "__main__":
    main()
