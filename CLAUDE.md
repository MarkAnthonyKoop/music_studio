# CLAUDE.md — music_studio

Read `README.md` first. Universal rules: `~/CLAUDE.md`. Machine notes: `~/claude/CLAUDE.md`.

## What this is

`music_studio` is the **only** project-level dir for music-release workflows. Past mistakes from earlier sessions:

- Defaulting CWD to `youtube_publisher/` because that's where some sessions started — wrong, that sibling owns YouTube uploads, not the whole workflow.
- Putting workflow scripts and artifacts in `/tmp/` — wrong, `/tmp/` is tmpfs and gets purged on WSL restart, taking your work with it.

The right home for "I'm doing a music release" is `~/claude/music_studio/runs/<song>-<date>/`. That's the cwd for the duration of the run.

## Run dirs are sacred

Each run gets its own subdir under `runs/`. Don't mix runs. Don't move scripts between runs — copy and edit. The handoff.md inside each run dir is the state-of-this-specific-release; treat it like a session log.

## What goes IN the run dir

- `handoff.md` — current state for resumption
- Workflow scripts (`compose_covers.py`, `upload_to_drive.py`, etc.) — small, per-run, edit-friendly
- Generated covers (`ai_covers/`, `composed_covers/`)
- Built MP4s (`mp4/`)
- Output JSONs from upload steps (`drive_links.json`, `youtube_results.json`)

## What does NOT go in the run dir

- Persistent stem audio + transcribed artifacts → `/mnt/d/downloads/suno_stems/<song>/`. Those are reproducible from Suno but expensive to regenerate; keep them on real disk.
- OAuth tokens → `~/.cache/youtube_publisher/`. Tokens are scoped to a Google project, not to a song.
- Reusable code — when a workflow script's logic shows up in 2+ runs, lift it into a sibling (`release_video/`, future `recipes/` module, etc.).

## Don't grow a config system

When the second run shows up, it's tempting to factor common values (artist name, label, cover style) into a YAML file. Resist for at least 3 runs. Per-run scripts that import the same constants from `youtube_publisher.metadata` are fine.

## Don't grow a top-level CLI yet

Until there are 3+ recipes that all look the same shape, a CLI is premature. Per-run shell pipelines (or a per-run `run.py`) are the right size.

## Workflow scripts stay under 100 lines each

If `upload_to_youtube.py` is creeping toward 150 lines, extract a function from it into a sibling. The script should read like a recipe, not a program.

## Smoke test

There's no canonical smoke test for `music_studio` itself — it's pure orchestration. But every leaf sibling it composes has one (see their CLAUDE.mds). When debugging a run, run the leaf's smoke test first to localize the failure.
