# 01_hillclimb rubric — FROZEN before first image, never edited mid-run

**Objective A: automotive studio hero shot.** Evolve "a dark grey sports coupe in a
photo studio" into a flagship-launch hero image through prompt mutation only.

**Start prompt:** `a dark grey sports coupe in a photo studio`
**Seed:** 424242 (fixed all run) · **Knobs:** positive prompt only
**Stop:** total-score spread < 2 over last 4 scored iterations, or n = 15

## Criteria (0–10 each, total /50)

### 1. paint_reflections
Highlight rolloff on body panels. Long, soft scrim/softbox reflections that follow
the body lines; smooth gradient falloff; no blown white streaks or crunchy speculars.
- 2 = flat or noisy paint, no readable light sources
- 5 = reflections present but broken, hot spots clipping
- 8 = continuous scrim lines along shoulder/hood, controlled rolloff
- 10 = production-grade: reflections model the surface curvature

### 2. separation_rim
Car separates cleanly from background. Rim/kicker light defines the silhouette on
roofline and rear quarter; no tonal merging of dark car into dark background.

### 3. materials
Paint, glass, chrome/brightwork, and rubber each read as distinct materials. Glass
has believable transmission/reflection; tires are diffuse, not glossy plastic.

### 4. composition_stance
Deliberate camera (3/4 front or profile), car grounded with correct contact shadow,
usable negative space, controlled background gradient/sweep. Wheels at rest or
intentionally styled — not mid-rotation smear.

### 5. technical
No warped badges, melted vents, wrong wheel geometry, doubled spokes, banding, or
AI artifacting. Symmetry where symmetry belongs.

## Judge protocol

Per iteration the judge (Claude this run; Hermes later) sees ONLY: this rubric, the
new image, and the score history — then appends one row to `logs/judge.jsonl`:

```json
{"n": 0,
 "scores": {"paint_reflections": 0, "separation_rim": 0, "materials": 0,
            "composition_stance": 0, "technical": 0},
 "total": 0,
 "notes": "what is limiting the score",
 "next_prompt": "the full mutated prompt for n+1",
 "rationale": "one line: what changed and which criterion it targets"}
```

Rules: score before writing the mutation; one primary criterion targeted per
mutation; never rewrite the whole prompt (mutate, don't restart); rubric text is
immutable once iteration 0 exists.
