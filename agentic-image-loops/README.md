# agentic image loops

Three experiments in iterative image generation with ComfyUI: an LLM agent in the
loop mutates prompts and judges results against frozen rubrics, while a dumb Python
runner drives a frozen workflow. Same grey coupe throughout: **hill-climbed** to a
studio hero shot (27 → 44/50), **morphed** onto a coastal highway without losing its
identity, and **evolved** through five generations of selection to 48/50 — every
prompt, seed and score logged.

**Live site:** enable GitHub Pages on this repo (Settings → Pages → deploy from
`main`, root) and the landing page is `index.html`.

## Results

| # | experiment | question | result |
|---|---|---|---|
| 01 | Hill-Climb | can prompt mutation + a frozen rubric climb quality? | 27 → 44/50 in 10 iterations, stopped by plateau rule |
| 02 | Morph | can an img2img chain travel studio → highway holding identity? | arrived in 7 clean beats; collapse case study preserved |
| 03 | Evolve | does population search beat single-lineage refinement? | 48/50 at generation 4, +4 over the hill-climb baseline |

## Architecture

**Code repeats, the agent decides.** A file-watching runner (`pipeline/loop.py`)
owns everything deterministic: inject prompt + seed into the frozen graph, submit to
ComfyUI, save the image, append one JSON line to the run log. The agent owns
everything requiring judgment: score the image against a rubric frozen before frame
0, write the next prompt mutation as a small JSON step file. The interface between
them is just files — swap the agent (frontier model, local Hermes, a human with
Notepad) and nothing else changes.

## Repository layout

```
index.html            landing page
experiments/          one detail page per experiment (every frame, prompt, score)
assets/               WebP frames (61 MB of PNG → 3 MB) + morph video
data/                 the raw record: run.jsonl, judge.jsonl, rubric.md per experiment
pipeline/             the actual machinery: loop.py runner, frozen workflow JSONs,
                      wait_for.py, analyze.py, make_report.py
tools/build_site.py   regenerates the entire site from data/ (stdlib only)
FINDINGS.md           cross-experiment lessons, grounded in the logs
```

## Reproducing

Requirements: ComfyUI on `127.0.0.1:8188` with Krea 2 Turbo fp8 (`krea2_turbo_fp8_scaled`,
`qwen3vl_4b_fp8_scaled` text encoder, `qwen_image_vae`), Python 3.10+, and any agent
that can read images and write JSON files.

1. Create a run folder containing a `rubric.md` (see `data/*/rubric.md` for the three used here).
2. Start the runner: `python pipeline/loop.py --run-dir <RUN>` (add
   `--workflow pipeline/workflow_api_i2i.json` for img2img experiments).
3. The agent writes `inbox/step_000.json` (`{"n":0,"prompt":"...","seed":...}`),
   waits via `pipeline/wait_for.py`, judges the image, appends to `logs/judge.jsonl`,
   and repeats until the rubric's stop condition fires.
4. `python tools/build_site.py` rebuilds the site from whatever is in `data/`.

## License

MIT — see [LICENSE](LICENSE). Images were generated with Krea 2 Turbo via ComfyUI.
