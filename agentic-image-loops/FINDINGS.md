# exp05 findings — hillclimb / morph / evolve

One frozen Krea2-turbo workflow, one dumb Python runner, three loop topologies.
Everything below was observed in the logs (`*/logs/*.jsonl`), not theorized.

## Headline results

| stage | question | answer |
|---|---|---|
| 01_hillclimb | can agent prompt-mutation + fixed rubric climb reliably? | yes: 27→44/50 in 10 iters, plateau detector fired correctly |
| 02_morph | can an i2i chain travel studio→highway holding identity? | yes: arrival in 7 clean beats, identity 10/10 throughout |
| 03_evolve | does population search beat single-lineage refinement? | yes: 48/50 vs 44/50, +4 in 5 generations (20 images) |

## Seed policy depends on loop topology (the biggest finding)

- **t2i refinement (hillclimb): FIX the seed.** Every visual change is then
  attributable to the prompt edit. Non-negotiable for judging the judge.
- **i2i chains (morph): ROTATE the seed every frame.** Fixed seed re-applies the
  identical noise pattern each step; artifacts correlate and lock in (our speckle
  storm, frames 0–3). One seed rotation broke a two-frame stall instantly.
- **evolution: seed IS a gene.** A seed reroll alone matched a 44 champion and
  deleted its seed-locked defect (gen 0, n2). Treat reroll as a mutation operator.

## Artifact recovery in i2i chains

- **Low denoise does NOT repair artifacts — it preserves them.** Denoise defends
  existing pixels, junk included. Our frozen "drop to 0.30 to recover" policy made
  speckle categorically worse in one step.
- What works, in order of preference: (1) roll back to the last clean ancestor and
  re-branch, (2) repaint at 0.50+ with fresh seed, (3) full chain restart. The car
  body always self-repaired before the background did — the model defends the
  subject, junk survives in low-attention regions.
- Artifacts trace to prompt wording: "floor beginning to lighten" birthed the wet
  speckle. Transitional/ambiguous surface language is a collapse seed.

## Layout attractors: relabel, don't fight

Compositions with strong structure (dark surround + bright center: our garage
doorway, then the bridge) survive any denoise you can afford. Negating them
("no overpass") does nothing. What works: **keep the structure, change its
meaning** — garage mouth → highway underpass mouth, in one 0.55 step, best beat
of the run. Describe what things ARE, not what should disappear.

## Prompt physics: cause, not effect

- "fine metal flake catching the light" → first 10/10 paint (the model has a
  physical reason for rich speculars). WON the evolution run.
- "reflections modeling every curve" / "a single sweep" → jagged, calligraphic
  junk, twice (n13, n17 in 03_evolve; n9 in 01_hillclimb). Art-directing the
  exact reflection shape over-constrains; describing material/light-source
  physics lets the sampler solve it.
- Style keywords move composition, not just quality: "professional advertising
  photograph" redesigned the entire car (hillclimb n6). Budget for that.
- Surface-quality clauses can hijack framing: "smooth uncluttered hood" pulled
  the camera high and tight, twice.

## Loop mechanics that proved out

- **Blackboard protocol** (agent writes step JSON, dumb runner executes, agent
  judges files): zero failures across 42 generations, fully agent-agnostic.
- **Rubric frozen before frame 0** kept 10-iteration score curves comparable;
  the plateau rule (spread < 2 over last 4) fired exactly when marginal gains
  died. Policy errors were handled as logged amendments, never silent edits.
- **Elitism** made evolution monotonic — fitness never regressed in 5 generations.
- **Crossover earned its keep**: both 46 and 47 champions were crossovers, fusing
  independently discovered wins (chrome grille line × clean hood line × low angle).
- Judge blind spots to watch: brand-identity drift (the model relaxes toward real
  production designs — BMW/Maserati/Aston) is invisible to this rubric.

## Numbers worth remembering (5090, Krea2-turbo fp8, 1664×928)

~7.5–8s per image; 8 steps, cfg 1, er_sde/sgm_uniform. Hillclimb run ≈ 9 min,
morph ≈ 2 min of generation, full 20-image evolution ≈ 3 min. Iteration is
effectively free — design experiments accordingly.
