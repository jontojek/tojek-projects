# tojek.com/projects

Source for the projects area of [tojek.com](https://tojek.com/projects/) — one small
AI / VFX / realtime experiment per folder, one folder per project.

## Structure

```
index.html            landing page (GENERATED — do not edit by hand)
build_index.py        generates index.html from each project's meta.json
assets/               landing-page thumbnails (small mp4 loops + poster jpgs)
<project>/            one folder per project, self-contained
  index.html            the project page
  meta.json              card data for the landing page
  _sources/               raw media (gitignored — never committed)
```

## Adding a project

1. Drop the project folder in (self-contained `index.html` plus its assets).
2. Create `<folder>/meta.json` — copy one from an existing project:
   `title`, `blurb`, `tags`, `date` (YYYY-MM-DD), `cta`, `thumb`.
3. Make a card thumbnail — 900px wide, 16:9. Prefer a short looping mp4
   (~5–10s, crf 28–32, target well under 500 KB) plus a poster jpg, into `assets/`.
4. `python build_index.py` — regenerates the landing page, newest first.
5. Commit and push.

## Media policy

Only web-ready assets are committed: compressed webp/jpg and small h264 mp4s.
Raw captures, 4K renders, .blend/.psd files etc. live in a `_sources/` folder
inside the project (gitignored) and are backed up outside git.

## Deployment

Hosted on Arvixe shared hosting; files go to `public_html/projects/`.
Currently deployed manually via cPanel File Manager. (Planned: automatic
deploy on push — cPanel Git Version Control or GitHub Actions FTPS sync.)
