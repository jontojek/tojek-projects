# HERMES HANDOFF: 58012 METHOD EXFOLIATOR NEUTRAL LOOKDEV
**Date:** 2026-07-22  
**Author:** Hermes Agent (tik1)  
**Target Reader:** Antigravity (Site Builder)  
**Context:** Internal LookDev presentation and narrative archive for the downstream RT/Compositing team (Stephanie Bouzard, Jacob Corrales) and 3D Artist (Patara Kornmai), 3D Manager (Ed Davis), Jon Tojek 3D/AI artist making the gel.

---

## 1. THE GOAL
This project represents a crucial **LookDev preparation pass** for the 58012 Generic Exfoliator product images, rather than the final branded, colored SKU hero images. 

Our main objective was to establish a perfect "neutral look" of the product tube and its exfoliating balm fill before any color-SKU tinting takes place. Specifically, we needed to generate clean, highly-controlled images of the **whipped body scrub balm inside the clear tube** to serve as a precise texture and lighting reference for the real-time (RT) retouching and CGI teams. 

This internal presentation website is built for:
*   **Stephanie Bouzard (Lead Compositor/Retoucher) and Jacob Corrales**, who need reference material to composite and color-tint the 10 final product SKUs in Photoshop/Nuke.
*   **Patara (3D Artist)**, who will use these material definitions to construct and calibrate the final CGI shaders in Maya/Nuke, under supervision from Ed Davis (3D Manager)
*   **Matt Clemens (Account Manager) and Nicole Segura (Project Manager)**, to track visual quality and alignment with Generic's standards.

---

## 2. WHAT "GOOD" MEANT (THE JUDGMENT CRITERIA)
Throughout this project, every generated render was evaluated against five rigorous, non-negotiable physical and aesthetic criteria:

1.  **Tube Plastic Specular Kill (The Hard Constraint):** The outer tube plastic must be 100% matte, non-reflective, and frosted. Any glossy sheen, bright specular highlight lines, or softbox reflections on the tube plastic were graded as immediate failures.
2.  **The "Crystal Look" Balm Fill:** The exfoliator inside is a thick, translucent crystalline balm (not a thin pink gel, and not a flat opaque foam). A successful render had to capture a luminous, slightly translucent quality that looks like light diffusing through frosted glass.
3.  **Micro-Aeration over Bubbles:** The suspended air pockets must be microscopic, soft-edged, and densely dispersed top-to-bottom. Renders with large, distinct spherical bubbles on the surface or empty air gaps at the walls failed. The fill must read as a dense, velvety, micro-porous silt—like pressed sand.
4.  **Subtle Ambient Frontal Lighting:** The unlit, dead-flat albedo pass approach was eventually abandoned. A "good" render allowed for just enough soft, diffuse frontal ambient lighting to convey the cylinder's 3D volume, while preserving complete compositing control.
5.  **Warm Off-White Chroma:** The base product color must reflect the real-world product's warm beige/off-white tone. Forcing a sterile, neutral grey was a failure.

---

## 3. THE STORY ARC (HOW THE LOOK EVOLVED)
### Phase 1: Decoding the Specs & Misdirection (v1–v5)
At kickoff (July 17), we worked off dieline briefs, assuming the gel was a sheer, translucent pink or blue with coarse speckled exfoliant grains. We even prepped for a "neutral green" clay proxy requested under Job Ticket 58012-1. However, everything changed when Jon inspected actual photos of the physical product. The real fill was not a sheer speckled gel; it was a thick, dense, warm off-white crystalline balm. We immediately locked this as our visual baseline in `material_spec_gel.md`.

### Phase 2: The Specular Battle & Albedo Dead End (v6–v11)
Jon began generating early iterations on Gemini Nano Banana 2. We immediately ran into our biggest technical hurdle: the AI generators insisted on drawing prominent, glossy vertical highlight lines down the sides of the tube. This happened because the model treated our shape reference as a photograph containing high-specular plastic. 

To combat this, we attempted an over-engineered "albedo pass" approach. We threw out photographic terminology and used render-engine syntax (`roughness = 1.0, specular = 0.0`) to force the highlights away. Unfortunately, this resulted in muddy, flat, and lifeless textures that lost all 3D volume and failed to guide the downstream team.

### Phase 3: The AI Studio Two-Layer Pivot (v12–v15)
On July 20, we pivoted to AI Studio running Gemini-3-pro-image. We designed a dual-layer prompt architecture: a permanent System Instruction containing strict physical material rules (instructing the model to convey volume through local-color boundaries, like making the tube wall slightly darker than the background, rather than using specular reflections) paired with a short, highly-focused text prompt. This allowed us to successfully separate 3D volume from glossy highlights.

### Phase 4: The Stephanie Handoff Breakthrough (v14–v16)
At our July 20th 3:00 PM handoff meeting, Lead Compositor Stephanie reviewed our `gel02_magnific_filled` batch. She approved the luminous, crystalline quality of files `0002`, `0003`, and `0006`. She gave a green light to "subtle ambient lighting" and warm chroma, but firmly re-established the ban on tube-plastic specular. She requested that we compress the bubble size even further. We pivoted to new micro-porous whipped balm references (`spread_gel_nightfall_v01.png`) and achieved a massive breakthrough with Magnific's GPT Image 2 model, completely eliminating edge specular lines.

### Phase 5: The Micro-Grain Sand Finish (v17–v18)
We executed a "Matte Refinement Reset" (v17) and "Micro-Grain Sand Refinement" (v18) using image-to-image workflows in AI Studio, seeding the generator with our approved favorites. By describing the texture as an ultra-dense, microscopic granular silt with the texture of pressed sand, we finally produced a flawless unlit matte sleeve holding a dense, luminous, micro-aerated crystalline balm.

---

## 4. THE PROJECT FOLDER MAP
To build the site gallery, you must understand the structure and naming of files in this project:

```
58012_Exfoliator_Product_Images/
├── 00_BRIEF/
│   ├── RT_handoff_2026-07-20.md          # RT meeting decisions & approved images
│   └── HTML_report_plan_2026-07-21.md    # Original blueprint for reporting
├── 01_reference/
│   ├── material_spec_gel.md              # Canonical material specifications
│   ├── job_ticket_58012-1.md             # Kickoff specs and original green proxy brief
│   └── images_gel/                       # Actual product photos (inside gel, spread gel)
├── 02_prompts/
│   └── neutral_bottle_nano_banana2.md    # Living prompt changelog (v1 to v18)
└── AI_generated/                         # Generated image outputs by epoch
    ├── gel01_magnific_gnb2/              # Epoch 1: Early exploration (v6). Glossy tube highlights.
    ├── gel02_magnific_filled/            # Epoch 2: Pre-sidecar era (v8-v10). Contains approved favorites 0002, 0003, 0006.
    ├── gel03_smaller_crystalline/        # Epoch 3: Smaller bubble trials (v15).
    └── gel04_spread/                     # Epoch 4: High-discipline Sidecar Era (v16-v18). Final matte/sand outputs.
```

### File-Naming Conventions & The Sidecar Protocol (Effective v18+)
Starting in Epoch 4 (`gel04_spread`), we established a strict sidecar protocol to prevent lost metadata. Every image file has a matching `.txt` sidecar containing its exact generation parameters:

`v{VERSION}_{SEQUENCE}_{GENERATOR}_{PLATFORM}.png`  
`v{VERSION}_{SEQUENCE}_{GENERATOR}_{PLATFORM}.txt`  

*   **VERSION:** The prompt version from our changelog (e.g., `v16`, `v17`, `v18`).
*   **SEQUENCE:** A 4-digit incremental counter (e.g., `0001`, `0002`).
*   **GENERATOR:** Model abbreviation (`gnb2` = Gemini Nano Banana 2, `gnbp` = Google Nano Banana Pro, `sd5p` = Stable Diffusion 5 Pro/Seedance, `gpt2` = GPT Image 2/Magnific).
*   **PLATFORM:** The interface used (`AIstudio` or `Magnific`).

**Example:** `v18_0001_gnbp_AIstudio.jpg` is accompanied by `v18_0001_gnbp_AIstudio.txt`, which outlines the system instructions, prompt text, seeds, and human QC notes.

---

## 5. PROJECT CHRONOLOGY (TIMELINE PHASES)
*   **Phase 1 (July 17): Kickoff & Spec Discrepancy**  
    Decoded dielines, wrote material specs, resolved Job Ticket 58012-1's "neutral green" proxy requirements. (v1–v5).
*   **Phase 2 (July 18–19): Early Renders & Bubble-to-Foam Transition**  
    First successful tube shapes. Transitioned from rendering particles/speckles to modeling suspended air foam. Hit the specular highlight wall. (v6–v8).
*   **Phase 3 (July 20): The Albedo Pass & AI Studio Pivot**  
    Engineered zero-specular prompts. Switched to AI Studio and introduced the two-layer System Instruction paradigm. (v9–v13).
*   **Phase 4 (July 20, 3:00 PM): Stephanie Handoff & Spec Lock**  
    RT Handoff Meeting. Stephanie locked files `0002`, `0003`, and `0006` from `gel02` as approved targets. Shifted from pure albedo back to soft ambient lighting. (v14–v15).
*   **Phase 5 (July 21): Micro-Porous Aeration & Specular Kill**  
    Introduced spread-gel reference, achieved highlight-free sleeve via GPT Image 2, and locked down the velvety micro-granular sand finish. (v16–v18).

---

## 6. WHERE MY JUDGMENTS & SCORES LIVE
*   **Approved Benchmarks:** Files `gen_filled_2k.0002.png`, `gen_filled_4k.0003.png`, and `gen_filled_4k.0006.png` in `AI_generated/gel02_magnific_filled/` represent the approved benchmarks from the RT Handoff meeting.
*   **The Sidecar QC Field:** Every sidecar `.txt` in `gel03` and `gel04` contains a `qc:` field (`pass`, `fail`, or `pending`) and a detailed `qc_notes:` section. This is where I annotated the images, grading them on specular highlights, bubble size, density, local-color separation, and structural silhouette.
*   **Historical Back-Propagation:** For the pre-sidecar images (0001–0006), I went back and manually generated estimated sidecar `.txt` files to document their performance in the RT meeting, ensuring the site can parse them uniformly.

---

## 7. CRITICAL GOTCHAS
*   **The "Green Leak" Shape Reference:** The shape reference file (`58012_AI_testing_jtojek_v1-02_LStop_2k.png`) is *green*. AI models will continuously try to turn your tube plastic or balm fill green because they inherit it from this image. You must explicitly instruct the generator that this reference is **SHAPE-ONLY** and to ignore its color.
*   **The Albedo Over-Correction:** Do not let the site frame the flat v10–v13 images as the target. They were an over-correction. The final approved spec uses *soft frontal ambient light*, not zero-light flat diffuse.
*   **Strict Sidecar Pairings:** Never mismatch or separate a `.png` from its matching `.txt` sidecar. The filenames are explicitly tied to preserve the chronological story of the prompt evolution.
*   **Warmth is Not a Mistake:** The warm off-white chroma of the balm in the final images is the approved real product color. It is not a color cast or an AI error; it is a deliberate client requirement.

---

## CANONICAL CONCLUSION
That behind every stunning, production-ready product image is an intense, disciplined technical battle to force generative AI to respect physical material constraints instead of default commercial beauty highlights.
