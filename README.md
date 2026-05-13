# music_studio

The orchestration sibling for music-release workflows. Composes the leaf siblings (`suno_client/`, `stem_transcriber/`, `cover_art/`, `ai_cover_art/`, `youtube_publisher/`, …) into multi-step pipelines like *download song → extract stems → transcribe → render covers → upload videos with artifact links*.

This package is intentionally thin. The leaf siblings do the work; `music_studio` just sequences them per a recipe.

---

## 1. User manual

There's no top-level CLI yet. Each release is its own **run** — a directory under `runs/` with the workflow scripts and ephemeral artifacts for that release:

```
~/claude/music_studio/
├── README.md
├── CLAUDE.md
└── runs/
    └── <song-slug>-<YYYY-MM-DD>/
        ├── handoff.md             — state of this specific run, for resumption
        ├── compose_covers.py      — workflow scripts, per-run for now
        ├── upload_to_drive.py
        ├── upload_to_youtube.py
        ├── ai_covers/             — generated artwork (raw)
        ├── composed_covers/       — final 1920×1080 with title overlay
        ├── mp4/                   — built videos
        └── drive_links.json       — populated after Drive upload
```

To start a run for a new song:

```bash
mkdir -p ~/claude/music_studio/runs/<song>-$(date +%F)
cd ~/claude/music_studio/runs/<song>-$(date +%F)
# crib from the latest sibling run dir, edit prompts/titles, then execute step by step.
```

Each run's `handoff.md` is written for the AI assistant doing the work — read it first.

---

## 2. Reference

### Why per-run scripts instead of one CLI

Each release has different cover prompts, different title patterns, different stem sets, sometimes different OAuth scopes. Making this generic would mean either an explosion of CLI flags or a config file, both of which violate "don't add what wasn't asked for." Per-run scripts are tiny (~50 lines each) and let you eyeball every line before it does something irreversible.

When the second run starts, copy the first run's scripts, edit the strings, and go. After a few runs you'll see what's truly reusable; *then* extract a `recipes/` module.

### Filesystem contract

- Each run has a self-contained dir under `runs/` — `cd` there to work.
- Persistent artifacts (mp3 stems, transcribed PDFs/MIDIs/tabs) live on `/mnt/d/downloads/suno_stems/<song>/` — NOT in the run dir. They survive WSL restarts; the run dir survives only if it's not on `/tmp`.
- Generated covers + MP4s live inside the run dir (not `/tmp`!) so they survive the workflow.

### Recipe outline (the canonical "release with stems" flow)

1. `suno_client.download` the original song + 12 stem clips → `/mnt/d/downloads/suno_stems/<song>/`
2. `stem_transcriber.transcribe` each stem (skip drums) → `<…>/transcribed/`
3. `ai_cover_art.generate` cover image per stem → `runs/<song>-<date>/ai_covers/`
4. `compose_covers.py` (PIL) — pad each cover to 1920×1080 + title overlay → `composed_covers/`
5. `ffmpeg` cover + audio → MP4 → `mp4/`
6. `upload_to_drive.py` — extend OAuth scope (one-time consent), upload artifacts, capture share links → `drive_links.json`
7. `upload_to_youtube.py` — build descriptions with Drive links, upload as scheduled-public via `youtube_publisher`

---

## 3. Architecture

```
~/claude/music_studio/
├── README.md
├── CLAUDE.md
└── runs/<song>-<date>/
    └── handoff.md, *.py, ai_covers/, composed_covers/, mp4/, drive_links.json
```

**Dependency direction:** `music_studio/runs/*` imports the leaf siblings (`suno_client`, `stem_transcriber`, `cover_art`, `ai_cover_art`, `youtube_publisher`). The leaves know nothing about `music_studio` — strict bottom-up.

### What belongs here vs a sibling

- **In here**: orchestration logic, per-release recipes, run state.
- **Sibling**: anything reusable across releases that isn't already a sibling — when one shows up, extract it. E.g. "build MP4 from cover + audio" is currently inline ffmpeg in `upload_to_youtube.py`; once we have a second run using it, lift to `release_video/`.

### Future work

- `recipes/` directory: once 3+ runs share a step, extract it as a reusable function.
- Top-level CLI: only after the recipe set stabilizes. Until then, per-run scripts.
- Run-status dashboard: probably a `status.py` in each run dir that reads `handoff.md` + `drive_links.json` + `youtube_results.json` and summarizes state. Useful when one run takes multiple sessions.
