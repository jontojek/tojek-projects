# exp06 — Autonomous IQA Evolution

Part of the [tojek-projects](../README.md) archive — see the root
[README](../README.md) and [HOW_THIS_WORKS.md](../HOW_THIS_WORKS.md) for how
this whole site is built and deployed.

## What this is

A 65-minute unattended evolution loop, run locally on an RTX 5090:

1. **ComfyUI** (`:8188`, KREA2 turbo checkpoint) renders a 1664×928 frame from
   the current prompt.
2. **PIL** scores it instantly on sharpness (Laplacian edge variance),
   colorfulness, and brightness.
3. A local **vision LLM judge in LM Studio** (`:1234`, 30B Qwen, 8B fallback)
   scores the frame out of 100, names its weakest criterion, and rewrites the
   prompt for the next generation.
4. Repeat.

Sixteen generations ran; four (#0009–#0012) hit GPU timeouts that the runner
caught and recovered from. The prompt drifted from a Voronoi stained-glass
mosaic seed to a vibrant mandala ceiling — candidate **#0004, score 95/100**,
the run's best performer.

## Files

- `index.html` — the self-contained report (timeline gallery, full candidate
  cards with prompts/metrics/critiques, run log)
- `media/thumb_*.webp` — grid thumbnails
- `media/big_cand_*.webp` — near-full-resolution images for the lightbox
  (swapped in for the original 2–2.8 MB PNGs on 2026-08-19; ~26 MB saved)
