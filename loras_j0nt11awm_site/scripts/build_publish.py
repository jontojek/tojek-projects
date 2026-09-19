"""Build the single-file publish version of the landing page.

    D:/AI_software/Fizgig/venv/Scripts/python.exe build_publish.py

Reads loras_j0nt11awm_site/index.html + media/, replaces every relative
media/ reference with a base64 data URI, and writes one file:

    loras_j0nt11awm_site_v02_publish/loras_j0nt11awm_v02.html

No sibling folders, no relative paths.
"""
from __future__ import annotations

import base64
import re
from pathlib import Path

SITE = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site")
PUB = Path(r"D:/AI_software/Fizgig/loras_j0nt11awm_site_v02_publish")
OUT_HTML = PUB / "loras_j0nt11awm_v02.html"

MIME = {".webp": "image/webp", ".mp4": "video/mp4", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def data_uri(path: Path) -> str:
    mime = MIME.get(path.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    html = (SITE / "index.html").read_text(encoding="utf-8")
    refs = sorted(set(re.findall(r'media/[A-Za-z0-9_.\-]+', html)))
    cache: dict[str, str] = {}
    total = 0
    for ref in refs:
        src = SITE / ref
        if not src.exists():
            raise SystemExit(f"referenced media missing: {src}")
        cache[ref] = data_uri(src)
        total += src.stat().st_size
        print(f"  {ref:38s} {src.stat().st_size/1024:8.1f} KB")
    for ref, uri in cache.items():
        html = html.replace(ref, uri)

    left = len(re.findall(r'media/', html))
    out = PUB
    out.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"\ninlined {len(refs)} assets ({total/1e6:.2f} MB raw)")
    print(f"residual 'media/' references: {left}")
    print(f"written: {OUT_HTML}  ({OUT_HTML.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
