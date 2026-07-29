# How my projects site works (the simple version)

*(For future me, when I've forgotten all of this.)*

## The one rule

**Never edit files on the server. Ever.** Everything happens in the local folder,
gets pushed to GitHub, and a robot copies it to the website automatically.

```
my PC  ──push──►  GitHub  ──robot──►  projects.tojek.com
(workbench)      (archive)            (the live site)
```

Whatever is on GitHub's `main` branch IS the website. If GitHub and the site
ever look different, wait two minutes — the robot is probably still copying.

## Adding a project (the daily routine)

1. Put the new project folder in `D:\AI_software\Github_repos\public_html_projects`
   (it needs its own `index.html`).
2. Copy a `meta.json` from any other project into the new folder, edit the
   title / blurb / tags / date. This is what makes its card appear.
3. Make a card thumbnail into `assets/` — a short looping mp4 + a poster jpg.
   (Or hand Claude a video/images and say "make the thumbnail".)
4. Run:  `python build_index.py`   ← this rebuilds the landing page
5. Commit everything and push (GitHub Desktop or command line, doesn't matter).
6. **That's it.** ~1 minute later the site is updated. No cPanel, no FTP, no zip.

## Things to remember

- **`index.html` at the root is GENERATED.** Never edit it by hand — edit the
  project's `meta.json` and re-run `build_index.py` instead.
- **Keep images small.** Convert big PNGs to webp before committing
  (Claude does this on request — "webp treatment"). Raw files (screen recordings,
  4K renders, .blend files) go in a `_sources/` folder inside the project —
  git ignores those automatically.
- **Deleting works too.** Remove a file from the repo, push, and the robot
  removes it from the site.

## When something looks wrong

1. Go to https://github.com/jontojek/tojek-projects/actions
2. Look at the newest run:
   - **Green check** = deploy worked. If the site looks stale, hard-refresh
     the browser (Ctrl+F5) — it's almost always your browser cache.
   - **Red X** = deploy failed. Open it, read the red step, or just show it
     to Claude.
3. The robot can also be run by hand: Actions → "Deploy to projects.tojek.com"
   → Run workflow.

## What the robot actually is

A GitHub Actions workflow (`.github/workflows/deploy.yml`). On every push to
`main` it logs into the Arvixe server over FTPS and syncs the repo into
`public_html/projects` — uploading what changed, deleting what I deleted,
skipping housekeeping files (README, build script, meta.json files).

Its login is an FTP account (`jont_deploy@projects.tojek.com`) that can ONLY
touch `public_html/projects` — the rest of tojek.com is out of its reach.
The password lives encrypted in GitHub → repo Settings → Secrets and variables
→ Actions. I can rotate it anytime: make a new password in cPanel → FTP
Accounts, update the `FTP_PASSWORD` secret, done.
