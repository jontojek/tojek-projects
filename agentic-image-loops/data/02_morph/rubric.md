# 02_morph rubric — FROZEN before frame 0, never edited mid-run

**Objective: directed morph.** Transport the studio hero shot (01_hillclimb iter_008)
to the target image (`target.jpg`: same grey coupe driving a coastal highway at
golden hour, ocean and trees, motion blur) through chained img2img steps.
Identity must survive the journey.

**Start frame:** `start_frame.png` (copy of 01_hillclimb/iterations/iter_008.png)
**Target reference:** `target.jpg` — used ONLY by the judge; never enters the workflow
**Seed:** 424242 fixed · **Knobs:** positive prompt + denoise (bounds 0.30–0.55)
**Chain:** frame N input = frame N-1 output (frame 0 input = start_frame.png)
**Stop (arrival):** trajectory_progress ≥ 9 AND identity_retention ≥ 7, or n = 20

## Criteria (0–10 each, total /40) — navigator, not scorer

### 1. identity_retention
Same car: body design, dark grey paint, wheel style, coupe proportions. 10 = could
be the same photographed vehicle; ≤6 = a different car is emerging.

### 2. step_continuity
Change from previous frame reads as one smooth beat of a camera move / scene
transition. 10 = seamless; ≤5 = jump cut (overshoot — consider lower denoise).

### 3. trajectory_progress
Distance covered toward the target scene (daylight, coastal road, nature, motion).
Score = how close THIS frame is to the target, 10 = arrived.

### 4. technical
No collapse artifacts: texture smearing, saturation drift, duplicated geometry,
melting details. Watch for cumulative i2i degradation across the chain.

## Denoise policy (agent follows, logs every change)

- Start at 0.40.
- identity_retention < 7 → drop 0.05 and add anchoring language (grey coupe, same car).
- trajectory_progress unchanged for 2 consecutive frames → raise 0.05 (max 0.55).
- technical < 6 → drop to 0.30 for one recovery frame with detail-restoring language.

## Judge protocol

Per frame the judge sees: this rubric, the new frame, the PREVIOUS frame, the
target image, and score history — then appends to `logs/judge.jsonl`:

```json
{"n": 0,
 "scores": {"identity_retention": 0, "step_continuity": 0,
            "trajectory_progress": 0, "technical": 0},
 "total": 0,
 "notes": "...",
 "next_prompt": "...", "next_denoise": 0.40,
 "rationale": "waypoint intent + any denoise change and why"}
```

Rules: score before mutating; prompts describe the CURRENT desired scene state
(not the final target) — waypoints, one beat ahead of the image; identity anchor
phrase appears in every prompt; rubric immutable once frame 0 exists.
