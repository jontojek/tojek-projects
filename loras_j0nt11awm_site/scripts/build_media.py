"""Build contact sheets + web thumbnails for the j0nt11awm LoRA landing page.

Run from anywhere:
    D:/AI_software/Fizgig/venv/Scripts/python.exe build_media.py sheets
    D:/AI_software/Fizgig/venv/Scripts/python.exe build_media.py thumbs

Nothing here is destructive: it only writes into the site's media/ folder.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None

SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
MEDIA = SITE / "media"
SCRATCH = SITE / "scripts" / "_scratch"

V02 = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_v02/images")
CLIPS = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_minimax/clips")


def list_images(d: Path) -> list[Path]:
    out = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        out.extend(sorted(d.glob(ext)))
    return out


def contact_sheet(paths: list[Path], out_path: Path, cols: int = 6, cell: int = 320,
                  label: bool = True) -> Path:
    if not paths:
        raise SystemExit(f"no images to sheet")
    rows = (len(paths) + cols - 1) // cols
    pad = 6
    sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + pad) + pad), (16, 17, 20))
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + pad)
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                im.thumbnail((cell, cell), Image.Resampling.LANCZOS)
                ox = x + (cell - im.width) // 2
                oy = y + (cell - im.height) // 2
                sheet.paste(im, (ox, oy))
        except Exception as e:  # noqa: BLE001
            draw.text((x + 8, y + 8), f"ERR {p.name}", fill=(220, 80, 80))
        if label:
            draw.text((x + 6, y + 6), f"{i+1}:{p.stem}", fill=(255, 235, 120))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=88)
    return out_path


def cmd_sheets() -> None:
    base = [p for p in list_images(V02) if not p.stem.startswith("FaceCrop")]
    crops = [p for p in list_images(V02) if p.stem.startswith("FaceCrop")]
    print(f"base images: {len(base)}  face crops: {len(crops)}")
    print(contact_sheet(base, SCRATCH / "sheet_v02_base.jpg", cols=6, cell=340))
    print(contact_sheet(crops, SCRATCH / "sheet_v02_crops.jpg", cols=6, cell=340))


def webp(src: Path, out_name: str, max_dim: int = 1400, quality: int = 86) -> Path:
    dst = MEDIA / out_name
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "WEBP", quality=quality, method=6)
    return dst


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheets"
    if cmd == "sheets":
        cmd_sheets()
    else:
        raise SystemExit(f"unknown command {cmd!r}")
