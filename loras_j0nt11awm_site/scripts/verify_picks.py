"""Build a labeled verification sheet from explicit training files.

    D:/AI_software/Fizgig/venv/Scripts/python.exe verify_picks.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None

V02 = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_v02/images")
SCRATCH = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site/scripts/_scratch")

CROPS = ["FaceCrop_004", "FaceCrop_012", "FaceCrop_015", "FaceCrop_001", "FaceCrop_024", "FaceCrop_026"]
BASE = ["jont09_0005", "jont09_0009", "jont09_0017", "jont09_0018", "jont09_0019", "jont09_0022",
        "jont09_0028", "jont09_0031", "jont09_0038", "jont09_0040"]


def find(stem: str) -> Path | None:
    for p in V02.glob(stem + ".*"):
        return p
    return None


def sheet(names: list[Path], out: Path, cols: int = 5, cell: int = 400) -> Path:
    rows = (len(names) + cols - 1) // cols
    pad = 8
    sh = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + pad) + pad), (14, 15, 18))
    d = ImageDraw.Draw(sh)
    for i, p in enumerate(names):
        r, c = divmod(i, cols)
        x, y = pad + c * (cell + pad), pad + r * (cell + pad)
        with Image.open(p) as im:
            im = im.convert("RGB")
            im.thumbnail((cell, cell), Image.Resampling.LANCZOS)
            sh.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.rectangle([x, y, x + cell, y + 22], fill=(0, 0, 0))
        d.text((x + 6, y + 5), p.stem, fill=(255, 220, 90))
    sh.save(out, "JPEG", quality=90)
    return out


if __name__ == "__main__":
    SCRATCH.mkdir(parents=True, exist_ok=True)
    crops = [find(n) for n in CROPS]
    bases = [find(n) for n in BASE]
    print(sheet([p for p in crops if p], SCRATCH / "verify_crops.jpg", cols=3, cell=460))
    print(sheet([p for p in bases if p], SCRATCH / "verify_base.jpg", cols=5, cell=400))
