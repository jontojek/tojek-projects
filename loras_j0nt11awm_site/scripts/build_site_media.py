"""Build the web media set for the j0nt11awm LoRA landing page.

    D:/AI_software/Fizgig/venv/Scripts/python.exe build_site_media.py

Sources:
  training stills  -> dataset/j0nt11_v02/images
  training clips   -> dataset/j0nt11_minimax/clips (first/mid frame extraction)
  rendered results -> scripts/_renders/krea2, scripts/_renders/h3

Writes WebP into loras_j0nt11awm_site/media/. Nothing outside the site is touched.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
MEDIA = SITE / "media"
RENDERS = SITE / "scripts" / "_renders"
SCRATCH = SITE / "scripts" / "_scratch"

V02 = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_v02/images")
CLIPS = Path(r"D:/AI_software/Fizgig/dataset/j0nt11_minimax/clips")

TRAIN_CROPS = ["FaceCrop_001", "FaceCrop_004", "FaceCrop_012", "FaceCrop_015", "FaceCrop_024", "FaceCrop_026"]
TRAIN_CTX = ["jont09_0005", "jont09_0009", "jont09_0017", "jont09_0018", "jont09_0019",
             "jont09_0022", "jont09_0028", "jont09_0031", "jont09_0038", "jont09_0040"]
# clip -> caption (read from the sidecar .txt beside it)
TRAIN_CLIPS = ["export005_iphone.0002b", "export005_iphone.0003b",
               "export005_iphone.0007b", "export005_iphone.0008b"]


def find(stem: str, folder: Path) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = folder / (stem + ext)
        if p.exists():
            return p
    return None


def save_webp(src: Path, out_name: str, max_dim: int = 1100, quality: int = 84) -> Path:
    dst = MEDIA / out_name
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "WEBP", quality=quality, method=6)
    return dst


def ffmpeg_frame(clip: Path, t: float, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-ss", f"{t}", "-i", str(clip), "-frames:v", "1", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dst.exists()


def cmd_build() -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []

    # 1. face crops - the likeness signal
    for stem in TRAIN_CROPS:
        p = find(stem, V02)
        if p:
            made.append(save_webp(p, f"train_crop_{stem.replace('FaceCrop_','')}.webp", max_dim=700))

    # 2. context stills - the variety
    for stem in TRAIN_CTX:
        p = find(stem, V02)
        if p:
            made.append(save_webp(p, f"train_ctx_{stem}.webp", max_dim=900))

    # 3. clip frame grabs - the video/voice dataset
    for i, stem in enumerate(TRAIN_CLIPS, 1):
        clip = CLIPS / f"{stem}.mp4"
        if not clip.exists():
            print(f"  ! clip missing: {clip}")
            continue
        tmp = SCRATCH / f"clipframe_{i}.png"
        if ffmpeg_frame(clip, 1.0, tmp):
            made.append(save_webp(tmp, f"train_clip_{i:02d}.webp", max_dim=800))

    # 4. rendered results
    for k in ("blazer", "portrait", "neon", "beach"):
        for tag in ("with", "without"):
            p = RENDERS / "krea2" / f"krea2_{k}_{tag}.png"
            if p.exists():
                made.append(save_webp(p, f"result_krea2_{k}_{tag}.webp", max_dim=1000))

    print(f"wrote {len(made)} webp files into {MEDIA}")
    for p in made:
        print(f"  {p.name:34s} {p.stat().st_size/1024:7.1f} KB")


if __name__ == "__main__":
    cmd_build()
