"""Render the 4 finalized Fog descriptions to a markdown file for manual paste."""
import json
from pathlib import Path

RUN = Path(__file__).parent
gh = json.loads((RUN / "github_links.json").read_text())
yr = json.loads((RUN / "youtube_results.json").read_text())

ARTIST = "Mark Nadon"
LABEL = "MiddleMatter Music"
RELEASE_DATE = "2026-05-06"
JAM = ("This version is easier to play. Anyone that wants to jam it w/ me, "
       "put a link to your channel with your tracks and we can swap files "
       "(or we could get together if you are in Centralish Texas...")
DESC_FILES = {
    "(Original Mix)": ["fog_original.mp3"],
    "(Guitar Stem)":  ["fog_guitar.pdf", "fog_guitar.tab", "fog_guitar_basic_pitch.mid",
                       "fog_guitar.musicxml", "fog_guitar_notes.tsv"],
    "(Drums Stem)":   [],
    "(Vocals Stem)":  ["fog_vocals.pdf", "fog_vocals_basic_pitch.mid",
                       "fog_vocals.musicxml", "fog_vocals_notes.tsv"],
}


def build(suffix, fnames):
    lines = [
        f"Fog {suffix} — by {ARTIST}",
        f"Released by {LABEL} · {RELEASE_DATE}",
        "",
        JAM,
        "",
        f"All stems & scores (GitHub): {gh['repo_url']}",
    ]
    if fnames:
        lines.append("")
        lines.append("Files for this stem:")
        for fn in fnames:
            url = gh["files"].get(fn)
            if url:
                lines.append(f"  - {fn}: {url}")
    if "(Drums" in suffix:
        lines.append("")
        lines.append("(Drum transcription artifacts pending — basic-pitch is bad at "
                     "drums; ADTOF integration is in progress.)")
    return "\n".join(lines)


out = [
    "# Fog YouTube descriptions to paste",
    "",
    "Open each video in YouTube Studio (links below) -> Details -> Description -> paste replace -> Save.",
    "",
    f"GitHub artifacts already uploaded: {gh['repo_url']}",
    "",
]

for entry in yr:
    title = entry["title"]
    suffix = next(s for s in DESC_FILES if s in title)
    desc = build(suffix, DESC_FILES[suffix])
    out.append(f"## {title}")
    out.append(f"- Watch: {entry['url']}")
    out.append(f"- Edit:  https://studio.youtube.com/video/{entry['id']}/edit")
    out.append("")
    out.append("```")
    out.append(desc)
    out.append("```")
    out.append("")

(RUN / "youtube_descriptions_to_paste.md").write_text("\n".join(out))
print("wrote", RUN / "youtube_descriptions_to_paste.md")
