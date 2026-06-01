# Run: studio-remix-2026-05-31

Take the last several Suno audio downloads, pull them into a Suno Studio project,
comp the best bits into something cool.

## Where the downloads were
`/mnt/c/Users/x/Downloads/` — Suno downloads land here, titled like
`138.5s Recording (May 31 @ 3_57 PM).mp3` (the duration-prefix "Recording" name is
Suno's export naming; ID3 `comment` confirms `made with suno`, artist `complexscenes6180`).

3 unique clips from today (a 4th file, `(2)`, was a byte-identical dupe):

| local copy | dur | Suno id | what it is (Suno's auto-description) |
|---|---|---|---|
| `src/clipA_0735am_51s.mp3` | 51s | c634f218 | Beatbox-driven hip-hop ~100bpm, G min — all vocal percussion + spoken word |
| `src/clipB_357pm_113s.mp3` | 113s | befcdd14 | Experimental spoken-word hip-hop (3:57pm take 1) |
| `src/clipC_357pm_121s.mp3` | 121s | d7dabd5e | Experimental spoken-word hip-hop (3:57pm take 2) |

B and C share title + creation timestamp → **two generations of the same 3:57pm song.**

## Analysis → editorial choices
`analysis/analyze.py` (librosa): tempo, key, RMS energy envelope, structural sections.
- B ≈ 117bpm A#min, C ≈ 112bpm Gmin (compatible, comp-able); A is the outlier (faster, beatbox).
- Output: `analysis/summary.json` + per-clip JSON + per-section energy ranks.

## The "something cool" — comp_BC (78s)
`out/build_edit.py` comps the strongest sections of the two sibling takes into one arc,
equal-power 0.6s crossfades, EBU R128 loudnorm. Arrangement:
1. clipC 0–13s   Gmin intro / mood
2. clipC 16–41s  Gmin main groove
3. clipB 18–37s  A#min build → peak/drop (key lift)
4. clipC 82–89s  Gmin punch hook
5. clipB 98–114s A#min resolve / outro

clipA (beatbox, different tempo/key) intentionally held out of the body → rendered
standalone as `out/optA.mp3` (its bright climax, 33s).

**Renders:** `out/comp_BC.{wav,mp3}`, `out/optA.{wav,mp3}`.
QC: comp_BC = −13.5 LUFS, −1.0 dBTP (no clip), no gaps, even energy.
Easy-play copies: `C:\Users\x\Downloads\COMP_best-bits_5-31.mp3` and `OPT-A_beatbox-climax_5-31.mp3`.

Caveat: built blind (I can't hear it). Section picks are energy/structure-driven.
Because the source is rhythmic spoken-word/beatbox (not melodic-harmony-dependent),
key shifts between sections are forgiving. Re-pick sections by editing `ARRANGEMENT`
in `build_edit.py` and re-running.

## Suno Studio project state
Driven via CDP Chrome (`computer_control/scripts`, port 9222) — signed in, Studio 1.2.
All 4 clips uploaded into the project **Library** ("Untitled Project"): clipA, clipB,
clipC, **comp_BC**. Each went through Studio's upload flow (Identify content → Full Song
→ accept AI description). They're playable in the library and ready to drag onto tracks.

**Not done:** auto-placing comp_BC as a region on the timeline track. Studio uses
cross-panel HTML5 drag (library → track lane); the library panel squeezes the lane
off-screen, so blind CDP drag isn't reliable. Manual: open the project, drag `comp_BC`
from the library onto Track 1. (Tried: library-click=preview only, double-click=no-op,
more-menu has no add-to-track.)

## Reusable helpers written this run
- `stage_upload.py` — drive one Studio upload end-to-end (file → tag → describe → Continue).
- `/tmp/cdp_shot.ps1` — one-shot CDP `Page.captureScreenshot` (the only way to actually
  SEE a CDP tab; `grab_screen.py` captures the foreground Windows window, not the tab).
  Worth lifting into `computer_control/scripts/` if screenshots recur.
