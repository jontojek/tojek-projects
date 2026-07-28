# 03_evolve rubric — FROZEN before generation 0, never edited mid-run

**Objective: beat the hill-climb.** Population search over prompt + seed space,
scored on the IDENTICAL rubric as 01_hillclimb (criteria below, verbatim, /50).
Baseline to beat: **44/50** (01_hillclimb n=7, seed 424242). The hill-climb proved
some defects are seed-locked (squiggly hood highlight); evolution makes seed part
of the search space.

## Scoring criteria — copied verbatim from 01_hillclimb/rubric.md

1. **paint_reflections** — highlight rolloff, continuous scrim sweeps, no clipping (0–10)
2. **separation_rim** — silhouette defined by rim/kicker, no tonal merging (0–10)
3. **materials** — paint/glass/brightwork/rubber read distinctly (0–10)
4. **composition_stance** — deliberate hero camera, grounded, controlled bg (0–10)
5. **technical** — no warped geometry, melted details, banding, artifacts (0–10)

## Evolution protocol

- **Population:** 4 variants per generation. **Budget:** 5 generations (20 images). t2i, fresh every time.
- **Generation 0:** v0 = champion prompt + champion seed 424242 (imported elite,
  anchors the baseline in-run); v1–v3 = one-clause mutations of the champion
  prompt, fresh seeds.
- **Selection:** score all 4; top 2 become parents.
- **Breeding (next gen):** 1 elite (champion unchanged, carried score), 2 single-clause
  mutations (one per parent, fresh seeds), 1 crossover (merge strongest clauses of
  both parents, fresh seed).
- **Mutation = exactly one of:** add a clause, remove a clause, reword a clause,
  or reroll seed only. Log the operator.
- **Stop:** end of generation 4, or any variant ≥ 48/50.

## Bookkeeping

Step numbering: n = generation*4 + variant. Judge rows add three fields:

```json
{"n": 0, "generation": 0, "variant": 0, "parent": "champion-01", "operator": "elite",
 "scores": {"paint_reflections": 0, "separation_rim": 0, "materials": 0,
            "composition_stance": 0, "technical": 0},
 "total": 0, "notes": "...", "prompt_used": "..."}
```

Rules: score each variant blind against the rubric before ranking the generation;
elitism is mandatory (fitness never regresses); every child's lineage and operator
logged; rubric immutable once generation 0 exists.

## Champion being attacked (01_hillclimb n=7, 44/50)

"professional automotive advertising photograph of a dark grey sports coupe in a
photo studio, low three-quarter front hero angle, dramatic low-key automotive
lighting, flawless mirror-polished paint with long elegant continuous highlight
sweeps along the body lines, dark gradient sweep background, crisp rim light
outlining the roofline and rear quarter panel, clean glossy black studio floor
with subtle mirror reflection, sharp detailed front grille, crisply machined
metal emblem, ultra sharp detail, no license plate"

Known weaknesses to attack: busy/squiggly hood highlight cluster (seed-locked at
424242), emblem sharpness, rocker falling to pure black.
