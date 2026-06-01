# obie-wan-2026-05-13 — "Introducing Obie Wan" demo

A rough proof-of-concept that takes a real 40-second clip of Obie playing
guitar at a coffee shop in S Austin, attaches a black-screen typewriter title
in front, and an AI-generated "flying / color-drain / crash" continuation
behind, scored by a Suno extension of Obie's actual live riff.

## Source clip

- `/mnt/d/downloads/there_is_no_homeless/VID_20260501_004914722.mp4`
- Captured 2026-04-30 19:49 CST, GPS 30.2562/-97.7462 (S 1st & Riverside).
- 40.4 s, 1080×1920 portrait (h264 with rotation=-90 metadata), AAC 256 kbps stereo.
- Symlinked to `raw/source.mp4` in this run dir.
- Audio extracted to `audio/obie_raw.wav` (the Suno seed).

## Constraints from the user

- Suno track must **continue Obie's actual live riff**, not start fresh.
- Light drums/bass OK but stay close to his harmonic/rhythmic feel —
  "not too much."
- Visuals are AI continuation; rough quality is fine (POC, not final).

## Timeline

| # | Section | Length | Source |
|---|---|---|---|
| 1 | Black + typewriter "Introducing Obie Wan_" | 5 s | `title/title.mp4` (rendered) |
| 2 | Raw footage (Obie at car, guitar, no lyrics) | 40 s | `raw/source.mp4` |
| 3 | AI: rise off ground, music kicks in | ~8 s | Runway shot 1 |
| 4 | AI: flying under control, lyrics start | ~10 s | Runway shot 2 |
| 5 | AI: color drains, loses control | ~10 s | Runway shot 3 |
| 6 | AI: tumble, crash, roll | ~8 s | Runway shot 4 |
| 7 | AI: sprawled, "without you" | ~5 s | Runway shot 5 |

Total ≈ 86 s. AI continuation = ~41 s.

## Lyrics

```
I don't see red
I don't see blue
I don't see green, or any hue
my world's all gray now
now without you
```

Lyric pacing (proposed):

| Line | Section | When |
|---|---|---|
| "I don't see red"             | shot 3 start  | color of red drains |
| "I don't see blue"            | shot 3 mid    | blue drains |
| "I don't see green, or any hue" | shot 3 end   | full grayscale lock |
| "my world's all gray now"     | shot 4        | tumble starts in grayscale |
| "now without you"             | shot 5        | sprawled, anguish |

## Suno extend — plan

Two paths. **Path A is the fast/safe one for the POC; path B is the long-term fix.**

### Path A — browser hand-off (recommended for POC)

1. User opens https://suno.com in Chrome.
2. Click **Upload Audio**, pick `audio/obie_raw.wav`.
3. Once processed, click **Extend** on it.
4. Title: `Obie Wan — fog of color`
5. Style tags: `acoustic folk, melancholy, lo-fi, sparse drums, subtle upright bass, no genre swing, continue the riff`
6. Lyrics (paste the block above).
7. Generate. Suno returns two takes; pick the better one.
8. Download the MP3/WAV into `audio/suno_extended.<ext>`.

Cost: included in the user's top-tier Suno subscription.

### Path B — API patch

`suno_client/generate.py:10` currently doesn't support continuation. The web
UI's network calls would tell us the exact payload shape — likely:

```python
payload = {
    ...generate_song fields...,
    "continue_clip_id": "<uploaded clip id from upload_audio()>",
    "continue_at": 40.0,  # seconds into the source where the extension starts
    "generation_type": "CONTINUE",
}
```

Add `continue_clip_id` and `continue_at` kwargs to `generate_song`. Test once
against the live API, adjust based on response. Out of scope for this run.

## Runway shots — prompts

The first shot uses `visuals/seed_liftoff.jpg` (last frame of the raw clip)
as the image-to-video seed. Each subsequent shot uses the *final frame of the
previous Runway output* as its seed — that's the only way Gen-3 keeps the
character consistent.

### Shot 1 — Liftoff (~5 s)
**Seed:** `visuals/seed_liftoff.jpg`
**Prompt:**

> A man in a straw cowboy hat, denim jacket, and grey t-shirt, still playing
> his acoustic guitar leaning against the back of a grey hatchback at night.
> Slowly he begins to levitate, feet rising off the pavement. Subtle wind in
> his hair. Continuous handheld camera. Realistic, cinematic, color, downtown
> Austin lights behind. Music carries him upward. No cuts.

**Negative:** cartoon, anime, distorted face, extra limbs, different person.

### Shot 2 — Flying under control (~10 s)
**Seed:** final frame of Shot 1
**Prompt:**

> Same man, straw hat, denim jacket, still playing the acoustic guitar, now
> soaring gracefully through the night sky over downtown Austin streetlights
> and low rooftops. Smooth, controlled motion. Hat brim catches the wind.
> Full color, cinematic wide shot from below. He sings along to the music.

### Shot 3 — Color drains, realization (~10 s)
**Seed:** final frame of Shot 2
**Prompt:**

> Same man flying, holding the acoustic guitar. The world around him
> desaturates in waves: red drains first, then blue, then green, until the
> entire scene is grayscale. His face shifts from joy to alarm as he notices
> the color leaving. Mid-air, suspended, hovering. Cinematic, dramatic.

### Shot 4 — Tumble + crash (~8 s)
**Seed:** final frame of Shot 3
**Prompt:**

> Same man losing control, tumbling head-over-heels through the gray sky,
> still gripping his acoustic guitar. Plummets toward a gray empty street
> below. Motion blur, dramatic, grayscale. Hits the pavement, rolls. Camera
> follows the fall.

### Shot 5 — Sprawled, "without you" (~5 s)
**Seed:** final frame of Shot 4
**Prompt:**

> Same man lying sprawled on his back on an empty gray street, straw hat
> tipped to one side, denim jacket disheveled, the acoustic guitar resting
> across his chest. He weakly strums it. Eyes half closed, mouth open in
> anguish. Camera slowly pulls up overhead. Grayscale, melancholy.

## What's blocking right now

- **Runway API key.** No key in env / cache / phones. Either mint one at
  https://dev.runwayml.com/ (paid) and paste, or you drive Runway's web UI
  yourself and we splice the outputs.
- **Suno auth (only if going Path B).** `chrome_auth` can't copy Chrome's
  cookie DB while Chrome is running with locks. Either close Chrome briefly
  (lose tab state) or launch the CDP profile and log into Suno there. Path A
  sidesteps this entirely.

## File layout (live)

```
obie-wan-2026-05-13/
├── plan.md                  ← this file
├── raw/
│   └── source.mp4           ← symlink to D: original
├── audio/
│   └── obie_raw.wav         ← extracted, Suno seed
├── title/
│   ├── render_title.py
│   ├── frames/*.png         ← 150 frames at 30fps
│   └── title.mp4            ← 5 s typewriter card (1080×1920)
├── visuals/
│   └── seed_liftoff.jpg     ← last frame of raw clip, Runway shot 1 seed
└── final/                   ← reserved for composited output
```
