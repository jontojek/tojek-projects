# VFX Space Shooter

A top-down 2D arcade space shooter in a single HTML file. HTML5 Canvas, vanilla JavaScript, zero dependencies.

## How to Play

Open `index.html` in Chrome. No server, no install — just double-click.

## Controls

| Key | Action |
|-----|--------|
| WASD or Arrow Keys | Move ship |
| SPACE | Fire (continuous, ~5.5 shots/sec) |
| R | Restart after game over |

## VFX Features

- **Neon Glow** — shadowBlur on ship, projectiles, and enemies
- **Particle Explosions** — additive-blended debris on enemy kills and player death
- **Motion Trails** — persistence-of-vision via semi-transparent frame fill
- **Starfield Parallax** — 3 depth layers drifting at different speeds
- **Screen Shake** — decaying camera offset on hits and explosions
- **Muzzle Flash** — white particle burst at ship nose on each shot
- **Chromatic Aberration** — RGB split flash on player damage

## Gameplay

- 3 enemy AI patterns: Hunter (tracks player), Diver (straight line), Weaver (sine sweep)
- Shield system: 100 HP, 3 hits to die, invulnerability frames after each hit
- Difficulty scales with score — faster enemies, tighter spawn rate

## Files

- `index.html` — the game
- `game_report.html` — full build report with screenshot, architecture, and agent metadata
- `game_screenshot.png` — headless Chrome capture
- `readme.md` — this file

## Built With

- Hermes Agent (Neko-chan v0.18.0) running MoA preset `moa_02_local`
- Aggregator: GLM 5.2 (api.engy.ai)
- Advisors: Tencent HY3 (Nous free tier), Qwen 3.6 35B Uncensored (local LM Studio)
