#!/usr/bin/env python3
"""Build the agentic-image-loops static site from data/*/(run|judge).jsonl.
Run from the repo root:  python tools/build_site.py
Outputs: index.html + experiments/*.html. Stdlib only."""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPS = [
    dict(id="01_hillclimb", slug="hillclimb", num="01", name="Hill-Climb",
         question="Can one-clause prompt edits, scored against a fixed rubric, steadily improve an image?",
         result="27 → 44/50 in ten iterations. The run stopped automatically when scores plateaued.",
         max_total=50, mode="txt2img · fixed seed", hero="iter_007",
         about=("This one is the control. The workflow and the seed never change, the scoring rubric is "
                "locked before the first image exists, and the agent is only allowed to edit one clause of "
                "the prompt per step. Score the frame, find the weakest thing about it, fix that one thing, "
                "repeat. Two defects survived every rewording attempted; experiment 03 was designed to test "
                "whether varying the seed could remove them.")),
    dict(id="02_morph", slug="morph", num="02", name="Morph",
         question="Can a chained img2img loop move the car from the studio to a coastal highway while keeping it the same car?",
         result="Arrived in seven steps. An early collapsed lineage is preserved in the logs and produced the clearest lessons.",
         max_total=40, mode="img2img chain · rotating seed", hero="iter_010",
         about=("Here each frame is generated from the previous one, so change accumulates. The agent writes "
                "waypoints - brighten the studio, open the garage door, out onto the road - always one beat "
                "ahead of where the image actually is. It gets one destination photo to steer toward, but "
                "that photo never touches the pipeline; it's for the judge's eyes only. The first attempt "
                "collapsed into speckle noise; every frame of that failure is kept below because it produced "
                "two of the most useful findings: fixed seeds cause artifacts to repeat in feedback chains, and low "
                "denoise preserves artifacts rather than repairing them.")),
    dict(id="03_evolve", slug="evolve", num="03", name="Evolve",
         question="Does population search — selection, mutation, crossover — outperform single-lineage refinement?",
         result="48/50 by generation four — four points above the hill-climb baseline.",
         max_total=50, mode="txt2img · population of 4 · seed as a gene", hero="iter_019",
         about=("A small genetic algorithm where the agent is the selection pressure. Four images per "
                "generation - different prompt tweaks, different seeds - and the best two get bred: one kept "
                "unchanged, two mutated, one crossover. In the first generation, a plain seed reroll matched the "
                "hill-climb champion, confirming that its persistent hood defect came from the seed, not the "
                "prompt. The highest-scoring image came from describing the paint material itself rather than "
                "the reflections it should produce.")),
]

CSS = """
:root{--bg:#101014;--panel:#18181e;--line:#26262e;--ink:#e6e6ea;--dim:#8b8b96;--acc:#ff7a45;--acc2:#ffb38a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif}
a{color:var(--acc2);text-decoration:none}a:hover{color:var(--acc)}
.wrap{max-width:1060px;margin:0 auto;padding:0 1.2rem}
header.site{padding:4.5rem 0 2.5rem;text-align:center}
h1{font-size:clamp(2rem,5vw,3.2rem);margin:.2rem 0;letter-spacing:-.02em}
.kicker{color:var(--acc);text-transform:uppercase;letter-spacing:.18em;font-size:.8rem;font-weight:600}
.sub{color:var(--dim);max-width:44rem;margin:.8rem auto 0}
.stats{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin:2rem 0 0}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:.35rem 1rem;font-size:.85rem;color:var(--dim)}
.chip b{color:var(--ink)}
section{padding:2.6rem 0}
h2{font-size:1.5rem;margin:0 0 1.2rem}
.split{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
@media(max-width:760px){.split{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.4rem}
.panel h3{margin:0 0 .5rem;font-size:1.05rem}
.panel .tag{font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;font-weight:700}
.tag.py{color:#6db3ff}.tag.ai{color:var(--acc)}
.panel p{color:var(--dim);margin:.4rem 0;font-size:.95rem}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
@media(max-width:900px){.cards{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;transition:transform .18s,border-color .18s}
.card:hover{transform:translateY(-4px);border-color:var(--acc)}
.card img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}
.card .body{padding:1.1rem 1.2rem 1.3rem;display:flex;flex-direction:column;gap:.5rem;flex:1}
.card .num{color:var(--acc);font-weight:700;font-size:.8rem;letter-spacing:.14em}
.card h3{margin:0;font-size:1.2rem}
.card .q{color:var(--dim);font-size:.92rem;flex:1}
.card .res{font-size:.88rem;border-top:1px solid var(--line);padding-top:.7rem}
.findings li{color:var(--dim);margin:.5rem 0}
.findings b{color:var(--ink)}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:.85rem;padding:2rem 0;margin-top:2rem;text-align:center}
.back{display:inline-block;margin:1.6rem 0 0;font-size:.9rem}
.attrs{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:.5rem;margin:1.4rem 0}
.attrs .k{color:var(--dim);display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em}
.iter{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.2rem;margin:1.2rem 0}
.iter h3{margin:.1rem 0 .8rem;font-size:1rem}.iter h3 span{color:var(--dim);font-weight:400;font-size:.85rem}
.iter img{width:100%;border-radius:8px}
.iter table{border-collapse:collapse;margin:.6rem 0}.iter td{padding:.12rem .9rem .12rem 0;color:var(--dim);font-size:.92rem}
.iter .tot td{color:var(--acc);font-weight:600}
.iter p{font-size:.93rem;color:var(--dim)}.iter p b{color:var(--ink)}
video{width:100%;border-radius:10px}
.tick{fill:var(--dim);font-size:11px}
p.md{color:var(--dim);max-width:52rem}
p.md b,li b{color:var(--ink)}
table.md{border-collapse:collapse;margin:1rem 0;width:100%;font-size:.92rem}
table.md th{text-align:left;color:var(--ink);border-bottom:1px solid var(--line);padding:.4rem .8rem .4rem 0}
table.md td{color:var(--dim);border-bottom:1px solid var(--line);padding:.4rem .8rem .4rem 0}
code{background:#1f1f27;border:1px solid var(--line);border-radius:5px;padding:.05rem .35rem;font-size:.88em}
"""


def read_jsonl(p):
    rows = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def esc(s):
    return html.escape(str(s))


def score_svg(points, max_total):
    if len(points) < 2:
        return ""
    w, h, pad = 760, 190, 36
    xs = [n for n, _ in points]
    x0, x1 = min(xs), max(xs)
    fx = lambda n: pad + (n - x0) / max(1, x1 - x0) * (w - 2 * pad)
    fy = lambda t: h - pad - (t / max_total) * (h - 2 * pad)
    poly = " ".join(f"{fx(n):.1f},{fy(t):.1f}" for n, t in points)
    dots = "".join(f"<circle cx='{fx(n):.1f}' cy='{fy(t):.1f}' r='4' fill='#ff7a45'/>"
                   f"<text x='{fx(n):.1f}' y='{fy(t)-10:.1f}' text-anchor='middle' class='tick'>{t}</text>"
                   for n, t in points)
    grid = "".join(f"<line x1='{pad}' y1='{fy(v):.1f}' x2='{w-pad}' y2='{fy(v):.1f}' stroke='#26262e' stroke-dasharray='3 4'/>"
                   f"<text x='{pad-8}' y='{fy(v)+4:.1f}' text-anchor='end' class='tick'>{v}</text>"
                   for v in range(0, max_total + 1, 10))
    xl = "".join(f"<text x='{fx(n):.1f}' y='{h-pad+18}' text-anchor='middle' class='tick'>{n}</text>" for n, _ in points)
    return (f"<svg viewBox='0 0 {w} {h}' style='width:100%'>{grid}"
            f"<polyline points='{poly}' fill='none' stroke='#ff7a45' stroke-width='2.5'/>{dots}{xl}</svg>")


def page(title, body):
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title><style>{CSS}</style></head><body>{body}</body></html>")


def build_detail(exp):
    d = os.path.join(ROOT, "data", exp["id"])
    run = {r["n"]: r for r in read_jsonl(os.path.join(d, "run.jsonl"))}
    judge = {r["n"]: r for r in read_jsonl(os.path.join(d, "judge.jsonl"))}
    ns = sorted(run)
    points = [(n, judge[n]["total"]) for n in ns if n in judge and "total" in judge[n]]
    gpu = round(sum(r.get("gen_time_s", 0) for r in run.values()), 1)

    attrs = {
        "mode": exp["mode"], "iterations": len(ns), "gpu time": f"{gpu}s",
        "best score": f"{max((t for _, t in points), default='—')}/{exp['max_total']}",
        "model": "Krea 2 Turbo fp8 · 8 steps · cfg 1", "resolution": "1664×928",
        "judge": "Claude, against a rubric frozen before frame 0",
    }
    attr_html = "".join(f"<div><span class='k'>{esc(k)}</span>{esc(v)}</div>" for k, v in attrs.items())

    extra = ""
    if exp["id"] == "02_morph":
        extra = ("<div class='iter'><h3>the full sequence as video</h3>"
                 "<video controls loop muted playsinline src='../assets/video/morph.mp4'></video>"
                 "<p>Clean lineage only: start → 4 → 6 → 7 → 8 → 9 → 10. The collapsed frames (0–3) and the stalled "
                 "frame (5) appear further down, unedited.</p></div>"
                 "<div class='iter'><h3>target reference <span>seen only by the judge — never entered the pipeline</span></h3>"
                 "<img src='../assets/img/morph/target.webp' loading='lazy'>"
                 "<p>Created separately (a Gemini img2img pass over the studio shot) to define the destination "
                 "the judge steers toward.</p></div>")

    cards = []
    for n in ns:
        r, j = run[n], judge.get(n)
        img = f"<img src='../assets/img/{exp['slug']}/iter_{n:03d}.webp' loading='lazy'>" if r.get("image") else \
              f"<p><b>ERROR:</b> {esc(r.get('error','?'))}</p>"
        meta = f"seed {esc(r['seed'])}"
        if "denoise" in r: meta += f" · denoise {esc(r['denoise'])}"
        if "i2i_input" in r: meta += f" · in: {esc(r['i2i_input'])}"
        if j and "generation" in j: meta += f" · gen {j['generation']} · {esc(j.get('operator',''))}"
        meta += f" · {esc(r.get('gen_time_s','?'))}s"
        jh = ""
        if j:
            rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}/10</td></tr>"
                           for k, v in j.get("scores", {}).items() if v is not None)
            jh = (f"<table>{rows}<tr class='tot'><td>total</td><td>{esc(j.get('total','?'))}/{exp['max_total']}</td></tr></table>"
                  f"<p><b>judge notes:</b> {esc(j.get('notes',''))}</p>")
            if j.get("rationale"):
                jh += f"<p><b>next mutation:</b> {esc(j['rationale'])}</p>"
        cards.append(f"<div class='iter'><h3>iteration {n:03d} <span>{meta}</span></h3>{img}"
                     f"<p><b>prompt:</b> {esc(r['prompt'])}</p>{jh}</div>")

    body = (f"<div class='wrap'><a class='back' href='../index.html'>← all experiments</a>"
            f"<header class='site' style='text-align:left;padding:1.6rem 0 0'>"
            f"<div class='kicker'>experiment {exp['num']}</div><h1>{esc(exp['name'])}</h1>"
            f"<p class='sub' style='margin-left:0'>{esc(exp['about'])}</p></header>"
            f"<div class='attrs'>{attr_html}</div>"
            f"{score_svg(points, exp['max_total'])}{extra}{''.join(cards)}"
            f"<footer>agentic-image-loops · MIT · rebuilt any time from data/{exp['id']}/*.jsonl</footer></div>")
    out = os.path.join(ROOT, "experiments", f"{exp['id']}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page(f"{exp['name']} — agentic image loops", body))
    return len(ns), gpu, max((t for _, t in points), default=0)


def build_index(stats):
    total_iters = sum(s[0] for s in stats)
    total_gpu = round(sum(s[1] for s in stats) / 60, 1)
    cards = ""
    for exp, st in zip(EXPS, stats):
        cards += (f"<a class='card' href='experiments/{exp['id']}.html'>"
                  f"<img src='assets/img/{exp['slug']}/{exp['hero']}.webp' loading='lazy' alt='{esc(exp['name'])} best frame'>"
                  f"<div class='body'><div class='num'>EXPERIMENT {exp['num']}</div><h3>{esc(exp['name'])}</h3>"
                  f"<div class='q'>{esc(exp['question'])}</div>"
                  f"<div class='res'>{esc(exp['result'])}</div></div></a>")
    body = f"""
<div class='wrap'>
<header class='site'>
  <div class='kicker'>agentic image loops</div>
  <h1>A fixed image pipeline.<br>An agent making the decisions.</h1>
  <p class='sub'>Three experiments in iterative image generation with ComfyUI. The workflow never changes;
  between frames, an LLM agent scores the image against a fixed rubric and writes the next prompt.
  The same grey coupe runs through all three: refined into a studio hero shot, moved from the studio
  onto a coastal highway through chained img2img, and improved further by selection and mutation
  across a population of prompts and seeds.</p>
  <div class='stats'>
    <span class='chip'><b>3</b> loop designs</span>
    <span class='chip'><b>{total_iters}</b> images generated</span>
    <span class='chip'><b>{total_gpu} min</b> of GPU, total</span>
    <span class='chip'><b>1</b> frozen workflow (Krea 2 Turbo)</span>
    <span class='chip'><b>every</b> decision logged</span>
  </div>
</header>

<section>
  <h2>How the work is divided</h2>
  <div class='split'>
    <div class='panel'><div class='tag py'>PYTHON</div>
      <h3>Everything that repeats is code</h3>
      <p>A small script watches a folder. When a prompt file appears, it runs it through the same frozen
      ComfyUI graph, saves the image, and appends one line to a log. It makes no judgment calls and never
      changes between runs, so results are repeatable and failures are easy to isolate.</p></div>
    <div class='panel'><div class='tag ai'>THE AGENT</div>
      <h3>Everything that requires judgment is the agent</h3>
      <p>Between frames, an LLM looks at the image, scores it against a rubric locked before the run
      started, and writes the next prompt as a small JSON file. The two halves communicate only through
      files on disk, so the agent can be swapped — a frontier model, a local model, or a person with a
      text editor — without changing anything else.</p></div>
  </div>
</section>

<section>
  <h2>The three experiments</h2>
  <div class='cards'>{cards}</div>
</section>

<section>
  <h2>What the logs taught us</h2>
  <ul class='findings'>
    <li><b>Seed handling depends on the loop type.</b> Fix the seed when refining a text-to-image prompt, so each change is attributable to the edit. Rotate it in img2img chains, where a fixed seed re-applies the same noise every frame and locks artifacts in. In evolution, treat the seed as one more variable to search.</li>
    <li><b>Low denoise preserves artifacts rather than repairing them.</b> When a chain degrades, roll back to a clean frame and regenerate at higher denoise. Experiment 02's collapsed lineage is preserved in full.</li>
    <li><b>Persistent compositions respond to relabeling, not force.</b> A garage doorway that held through every denoise setting changed immediately once the prompt described the same shape as a highway underpass.</li>
    <li><b>Describe the cause, not the desired result.</b> "Fine metal flake catching the light" produced the highest-scoring paint of the project; specifying the exact reflection shapes degraded the image every time it was tried.</li>
  </ul>
  <p style='color:var(--dim)'>The full write-up is on the <a href='findings.html'>findings page</a>.
  Every prompt, seed, score and judge note is in <code>data/</code>, unedited.</p>
</section>

<footer>agentic-image-loops · MIT · images generated locally with Krea 2 Turbo in ComfyUI · site rebuilt from data/ by tools/build_site.py</footer>
</div>"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("agentic image loops — hill-climb · morph · evolve", body))


def md_inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\\1</code>", s)
    return s


def md_to_html(md):
    out, in_list, table = [], False, []

    def flush_table():
        nonlocal table
        if table:
            head = "".join(f"<th>{md_inline(c)}</th>" for c in table[0])
            rows = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>"
                           for r in table[2:] if r)
            out.append(f"<table class='md'><tr>{head}</tr>{rows}</table>")
            table = []

    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("|"):
            table.append([c.strip() for c in s.strip("|").split("|")])
            continue
        flush_table()
        if s.startswith("- "):
            if not in_list:
                out.append("<ul class='findings'>"); in_list = True
            out.append(f"<li>{md_inline(s[2:])}</li>")
            continue
        if in_list and (s.startswith("  ") and s.strip()):
            out[-1] = out[-1][:-5] + " " + md_inline(s.strip()) + "</li>"
            continue
        if in_list:
            out.append("</ul>"); in_list = False
        if s.startswith("## "):
            out.append(f"<h2>{md_inline(s[3:])}</h2>")
        elif s.startswith("# "):
            pass  # page supplies its own h1
        elif s.strip():
            out.append(f"<p class='md'>{md_inline(s)}</p>")
    if in_list:
        out.append("</ul>")
    flush_table()
    # merge consecutive paragraph fragments (markdown soft wraps)
    def polish(s):  # catch inline marks that spanned a soft line-wrap
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\\1</b>", s)
        return s

    merged, buf = [], None
    for piece in out:
        if piece.startswith("<p class='md'>"):
            frag = piece[len("<p class='md'>"):-len("</p>")]
            buf = frag if buf is None else buf + " " + frag
        else:
            if buf is not None:
                merged.append(f"<p class='md'>{polish(buf)}</p>"); buf = None
            merged.append(polish(piece))
    if buf is not None:
        merged.append(f"<p class='md'>{polish(buf)}</p>")
    return "\n".join(merged)


def build_findings():
    md_path = os.path.join(ROOT, "FINDINGS.md")
    if not os.path.exists(md_path):
        return
    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    body = (f"<div class='wrap'><a class='back' href='index.html'>← all experiments</a>"
            f"<header class='site' style='text-align:left;padding:1.6rem 0 1rem'>"
            f"<div class='kicker'>the write-up</div><h1>Findings</h1>"
            f"<p class='sub' style='margin-left:0'>Cross-experiment lessons, taken from the run logs "
            f"rather than theory. The raw records are in <code>data/</code>.</p></header>"
            f"{md_to_html(md)}"
            f"<footer>agentic-image-loops · MIT · this page is generated from FINDINGS.md</footer></div>")
    with open(os.path.join(ROOT, "findings.html"), "w", encoding="utf-8") as f:
        f.write(page("findings — agentic image loops", body))


def main():
    stats = [build_detail(e) for e in EXPS]
    build_index(stats)
    build_findings()
    print("built index.html +", ", ".join(f"experiments/{e['id']}.html" for e in EXPS))


if __name__ == "__main__":
    main()
