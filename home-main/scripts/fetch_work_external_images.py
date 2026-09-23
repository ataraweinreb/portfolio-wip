#!/usr/bin/env python3
"""
Download externally hosted Work-section hero images and save as WebP locally.

Re-run if you change remote URLs in index.html. From repo root:
  .venv/bin/python scripts/fetch_work_external_images.py
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

WEBP_QUALITY = 90

# Longest edge cap — aligned with optimize_images.py hero assets (sharp at high zoom).
MAX_BOX = (1800, 1800)

# (output_stem, primary_url, fallback_url_or_none)
SOURCES: list[tuple[str, str, str | None]] = [
    (
        "work-snapchat-creators",
        "https://img.youtube.com/vi/PiKg9DTusHQ/maxresdefault.jpg",
        "https://img.youtube.com/vi/PiKg9DTusHQ/hqdefault.jpg",
    ),
    (
        "work-scan-multimodal",
        "https://img.youtube.com/vi/lrR7nc_rHJE/maxresdefault.jpg",
        "https://img.youtube.com/vi/lrR7nc_rHJE/hqdefault.jpg",
    ),
    (
        "work-food-scan",
        "https://images.ctfassets.net/o1znirz7lzo4/2klNhNeZWrSWMHJMNz92jl/f054091269d4cf8199565ffc915a324b/Untitled_presentation__1_.jpg?fm=jpg&q=90&h=2400",
        None,
    ),
    (
        "work-design-engineering",
        "https://images.ctfassets.net/7w2tf600vbko/16tOH0imttI0D4nn04bveD/ae6bea3fcc1281cbe222538d10cdd46f/JM1_8958__1_.jpg?fm=jpg&q=90&h=2400",
        None,
    ),
]

UA = "Mozilla/5.0 (compatible; personal-site-cache/1.0)"


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=120) as resp:
        return resp.read()


def to_webp(data: bytes, out: Path) -> None:
    im = Image.open(BytesIO(data)).convert("RGBA")
    im.thumbnail(MAX_BOX, Image.Resampling.LANCZOS)
    im.save(out, format="WEBP", quality=WEBP_QUALITY, method=6, lossless=False)


def main() -> None:
    for stem, primary, fallback in SOURCES:
        out = ROOT / f"{stem}.webp"
        try:
            raw = fetch(primary)
        except HTTPError:
            if fallback:
                raw = fetch(fallback)
            else:
                raise
        to_webp(raw, out)
        print(f"Wrote {out.relative_to(ROOT)}")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
