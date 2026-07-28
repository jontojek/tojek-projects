#!/usr/bin/env python3
"""Build summary.html for a run: attributes header, optional target-reference
card (from run_meta.json), score curve (inline SVG, file://-safe, no CDN), one
card per iteration (image, input prompt, judge scores/notes, mutation
rationale). Stdlib only. Regenerate any time:

  python make_report.py --run-dir ..\\02_morph_v01 [--max-total 40]
"""
import argparse
import html
import json
import os


def read_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def esc(s):
    return html.escape(str(s))


def score_svg(points, max_total=50, w=760, h=180, pad=34):
    if len(points) < 2:
        return "<p class='muted'>score curve appears after 2+ scored iterations</p>"
    xs = [n for n, _ in points]
    x0, x1 = min(xs), max(xs)
    fx = lambda n: pad + (n - x0) / max(1, x1 - x0) * (w - 2 * pad)
    fy = lambda t: h - pad - (t / max_total) * (h - 2 * pad)
    poly = " ".join(f"{fx(n):.1f},{fy(t):.1f}" for n, t in points)
    dots = "".join(
        f"<circle cx='{fx(n):.1f}' cy='{fy(t):.1f}' r='4' fill='#e8734a'/>"
        f"<text x='{fx(n):.1f}' y='{fy(t) - 10:.1f}' text-anchor='middle' class='tick'>{t}</text>"
        for n, t in points)
    grid = "".join(
        f"<line x1='{pad}' y1='{fy(v):.1f}' x2='{w - pad}' y2='{fy(v):.1f}' stroke='#333' stroke-dasharray='3 4'/>"
        f"<text x='{pad - 8}' y='{fy(v) + 4:.1f}' text-anchor='end' class='tick'>{v}</text>"
        for v in range(0, max_total + 1, 10))
    xlabels = "".join(
        f"<text x='{fx(n):.1f}' y='{h - pad + 18}' text-anchor='middle' class='tick'>{n}</text>"
        for n, _ in points)
    return (f"<svg viewBox='0 0 {w} {h}' style='width:100%;max-width:{w}px'>{grid}"
            f"<polyline points='{poly}' fill='none' stroke='#e8734a' stroke-width='2.5'/>"
            f"{dots}{xlabels}</svg>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--max-total", type=int, default=None,
                    help="score scale; default: read from run_meta.json or 50")
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)

    run = {r["n"]: r for r in read_jsonl(os.path.join(run_dir, "logs", "run.jsonl"))}
    judge = {r["n"]: r for r in read_jsonl(os.path.join(run_dir, "logs", "judge.jsonl"))}
    ns = sorted(run)
    name = os.path.basename(run_dir)

    # optional run_meta.json: {"target_image", "target_caption", "max_total", ...}
    meta = {}
    meta_path = os.path.join(run_dir, "run_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    max_total = args.max_total or meta.get("max_total") or 50

    target_html = ""
    if meta.get("target_image"):
        target_html = (
            "<section class='card'><h2>target reference</h2>"
            f"<a href='{esc(meta['target_image'])}'><img src='{esc(meta['target_image'])}' loading='lazy'></a>"
            f"<p>{esc(meta.get('target_caption', ''))}</p></section>")

    first = run[ns[0]] if ns else {}
    total_time = round(sum(r.get("gen_time_s", 0) for r in run.values()), 1)
    points = [(n, judge[n]["total"]) for n in ns if n in judge and "total" in judge[n]]

    attrs = {
        "model": "Krea 2 Turbo fp8 (official ComfyUI template, enhancer/LoRA off)",
        "sampler": f"{first.get('sampler', '?')} · {first.get('steps', '?')} steps · cfg {first.get('cfg', '?')}",
        "resolution": f"{first.get('width', '?')}×{first.get('height', '?')}",
        "mode": "img2img chain" if any("denoise" in r for r in run.values()) else "txt2img",
        "iterations": len(ns),
        "total gen time": f"{total_time}s",
        "best score": max((t for _, t in points), default="—"),
    }
    if meta.get("judge_agent"):
        attrs["judge"] = meta["judge_agent"]
    attr_html = "".join(f"<div><span class='k'>{esc(k)}</span><span class='v'>{esc(v)}</span></div>"
                        for k, v in attrs.items())

    cards = []
    for n in ns:
        r, j = run[n], judge.get(n)
        img = (f"<a href='{esc(r['image'])}'><img src='{esc(r['image'])}' loading='lazy'></a>"
               if r.get("image") else f"<div class='err'>ERROR: {esc(r.get('error', '?'))}</div>")
        extra = f" · denoise {esc(r['denoise'])}" if "denoise" in r else ""
        extra += f" · in: {esc(r['i2i_input'])}" if "i2i_input" in r else ""
        jhtml = "<p class='muted'>not judged</p>"
        if j:
            rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}/10</td></tr>"
                           for k, v in j.get("scores", {}).items() if v is not None)
            jhtml = (f"<table>{rows}<tr class='tot'><td>total</td><td>{esc(j.get('total', '?'))}/{max_total}</td></tr></table>"
                     f"<p><b>judge notes:</b> {esc(j.get('notes', ''))}</p>")
            if j.get("rationale"):
                jhtml += f"<p><b>next mutation:</b> {esc(j['rationale'])}</p>"
        cards.append(f"""
<section class='card'>
  <h2>iteration {n:03d} <span class='muted'>seed {esc(r['seed'])}{extra} · {esc(r.get('gen_time_s', '?'))}s</span></h2>
  {img}
  <p><b>input prompt:</b> {esc(r['prompt'])}</p>
  {jhtml}
</section>""")

    page = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>{esc(name)} — exp05 summary</title>
<style>
 body{{background:#141414;color:#ddd;font:15px/1.5 system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
 h1{{font-size:1.4rem}} h2{{font-size:1.05rem;margin:.2rem 0 .6rem}}
 .attrs{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.4rem;margin:1rem 0}}
 .attrs .k{{color:#888;display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}}
 .card{{background:#1d1d1d;border:1px solid #2c2c2c;border-radius:10px;padding:1rem;margin:1.2rem 0}}
 img{{width:100%;border-radius:6px}}
 table{{border-collapse:collapse;margin:.5rem 0}} td{{padding:.15rem .8rem .15rem 0;color:#bbb}}
 .tot td{{color:#e8734a;font-weight:600}} .muted{{color:#777}} .tick{{fill:#888;font-size:11px}}
 .err{{color:#e86a6a;background:#2a1a1a;padding:.6rem;border-radius:6px}}
</style></head><body>
<h1>{esc(name)} — run summary</h1>
<div class='attrs'>{attr_html}</div>
{target_html}
{score_svg(points, max_total)}
{''.join(cards)}
</body></html>"""

    out = os.path.join(run_dir, "summary.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out} ({len(ns)} iterations, {len(points)} judged)")


if __name__ == "__main__":
    main()
