# tojek-projects

> **Forgot how this all works? Read [HOW_THIS_WORKS.md](HOW_THIS_WORKS.md) — the 90-second version.**

This repo is the source for **[projects.tojek.com](https://projects.tojek.com/)** —
my public gallery of small daily AI / VFX / realtime experiments. One folder here =
one project = one card on the landing page.

## The big picture

Three places, three jobs:

| Place | Job |
|---|---|
| `D:\AI_software\Github_repos\public_html_projects` (this folder) | **Workbench.** Where projects get built and the landing page gets generated. |
| [github.com/jontojek/tojek-projects](https://github.com/jontojek/tojek-projects) | **Archive.** Every version of everything, forever. Pushing here is the backup. |
| [projects.tojek.com](https://projects.tojek.com/) | **The show.** Arvixe shared hosting; files get uploaded there via cPanel. |

The flow is always in one direction: build locally → commit & push to GitHub →
upload to the server. If my machine dies, GitHub has everything. If the server
dies, GitHub has everything. GitHub is the source of truth.

## How the landing page works

I never edit `index.html` by hand — it's **generated**. Every project folder
contains a small `meta.json` file that describes its card:

```json
{
  "title":  "VFX Space Shooter",
  "blurb":  "one-paragraph pitch shown on the card",
  "tags":   ["HTML5 Canvas", "Vanilla JS"],
  "date":   "2026-07-13",
  "cta":    "Play it",
  "thumb":  { "video": "assets/thumb_shooter.mp4",
              "poster": "assets/thumb_shooter_poster.jpg",
              "alt": "description for screen readers" }
}
```

Running `python build_index.py` scans every folder for a `meta.json` and rebuilds
`index.html` — newest project first, with a date badge on each card. So adding
project #37 never means touching the landing page's HTML; the card grid grows by
itself.

Card thumbnails are short **looping mp4s** (5–10 s, 900px wide, 16:9), not GIFs —
they look better and load faster (all four current ones total under 800 KB).
They live in the root `assets/` folder, next to a poster jpg that shows while
the video loads.

## Adding a new project (the daily routine)

1. Drop the project folder in — self-contained `index.html` plus whatever it needs.
2. Copy a `meta.json` from another project and fill in the fields.
3. Make the card thumbnail into `assets/` (short mp4 loop + poster jpg).
4. Rebuild and archive:
   ```
   python build_index.py
   git add -A
   git commit -m "Add project: <name>"
   git push
   ```
5. Upload the new/changed files to the server via cPanel File Manager.
   (Step 5 is temporary — see Deployment below.)

## Media policy — keep the repo light and the site fast

**Only web-ready files are committed:** compressed jpg/webp images and small
h264 mp4s. Raw material — screen captures, 4K renders, .blend files, PSDs —
goes in a `_sources/` folder inside the project, which `.gitignore` keeps out
of the repo entirely. Raw sources get backed up outside git (Drive/NAS).

Why: GitHub gets slow and unhappy with multi-GB repos, and a daily project
cadence would get there fast. The published site never needs the raw files —
today's 11 MB screen capture became a 161 KB thumbnail.

## Deployment

The site lives on Arvixe shared hosting (cPanel). Right now deployment is
manual: upload changed files through the cPanel File Manager.

Planned upgrade: connect the server to this GitHub repo (cPanel has a built-in
Git feature) so a push to `main` deploys automatically — making step 5 above
disappear.

## Related

- [tojek.com](https://tojek.com) — main site
- [vfx.tojek.com](https://vfx.tojek.com) — VFX reel/subdomain
