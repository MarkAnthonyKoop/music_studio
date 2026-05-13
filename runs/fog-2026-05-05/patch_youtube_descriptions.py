"""Patch the 4 already-uploaded Fog video descriptions with GitHub artifact links.

Reads ./youtube_results.json (video IDs) + ./github_links.json (file URLs).
Reuses the description template from upload_to_youtube.py, now with links.

Requires the cached token to have youtube.force-ssl scope (videos.update).
If it doesn't, get_credentials with the broader scope set will trigger a
one-time consent flow; complete it in Profile 10 and re-run.

Usage:
    python3 patch_youtube_descriptions.py [--dry-run]
"""
import argparse
import json
import sys
from pathlib import Path

from youtube_publisher.auth import get_credentials
from googleapiclient.discovery import build

RUN_DIR = Path(__file__).parent
CLIENT_SECRETS = "/mnt/c/Users/x/Downloads/client_secret_677495352-q1duspp6rlpo0gehpqrlq41rvf08o95f.apps.googleusercontent.com.json"

ARTIST = "Mark Nadon"
LABEL = "MiddleMatter Music"
RELEASE_DATE = "2026-05-06"

# Map title-suffix → (mp4 stem, list of github file names to link)
DESC_FILES = {
    "(Original Mix)": ["fog_original.mp3"],
    "(Guitar Stem)":  ["fog_guitar.pdf", "fog_guitar.tab", "fog_guitar_basic_pitch.mid",
                       "fog_guitar.musicxml", "fog_guitar_notes.tsv"],
    "(Drums Stem)":   [],
    "(Vocals Stem)":  ["fog_vocals.pdf", "fog_vocals_basic_pitch.mid",
                       "fog_vocals.musicxml", "fog_vocals_notes.tsv"],
}

JAM_INVITATION = (
    "This version is easier to play. Anyone that wants to jam it w/ me, "
    "put a link to your channel with your tracks and we can swap files "
    "(or we could get together if you are in Centralish Texas..."
)

SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
)


def build_description(suffix: str, file_names: list[str], gh: dict) -> str:
    lines = [
        f"Fog {suffix} — by {ARTIST}",
        f"Released by {LABEL} · {RELEASE_DATE}",
        "",
        JAM_INVITATION,
        "",
        f"All stems & scores (GitHub): {gh['repo_url']}",
    ]
    if file_names:
        lines.append("")
        lines.append("Files for this stem:")
        for fn in file_names:
            url = gh["files"].get(fn)
            if url:
                lines.append(f"  • {fn} — {url}")
    if "(Drums" in suffix:
        lines.append("")
        lines.append("(Drum transcription artifacts pending — basic-pitch is bad at "
                     "drums; ADTOF integration is in progress.)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    yt_results = json.loads((RUN_DIR / "youtube_results.json").read_text())
    gh = json.loads((RUN_DIR / "github_links.json").read_text())

    creds = get_credentials(client_secrets_path=CLIENT_SECRETS,
                            scopes=SCOPES, open_browser=False)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    for entry in yt_results:
        vid = entry["id"]
        title = entry["title"]
        suffix = next(s for s in DESC_FILES if s in title)
        new_desc = build_description(suffix, DESC_FILES[suffix], gh)

        cur = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
        body = {"id": vid, "snippet": {
            "title": cur["title"],
            "description": new_desc,
            "categoryId": cur["categoryId"],
            "tags": cur.get("tags", []),
        }}
        if args.dry_run:
            print(f"--- {title} ({vid}) ---\n{new_desc}\n")
            continue
        yt.videos().update(part="snippet", body=body).execute()
        print(f"  patched {title} ({vid})", file=sys.stderr)


if __name__ == "__main__":
    main()
