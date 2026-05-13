"""Upload the 4 Fog MP4s to YouTube as plain public releases.

Uses the cached youtube.upload-scoped token at
~/.cache/youtube_publisher/token_*.pickle — no Chrome consent needed.

Usage:
    python3 upload_to_youtube.py [--dry-run]
"""
import argparse
import json
import sys
from pathlib import Path

from youtube_publisher.upload import upload_video, PRIVACY_PUBLIC


ARTIST = "Mark Nadon"
LABEL = "MiddleMatter Music"
RELEASE_DATE = "2026-05-06"
RUN_DIR = Path(__file__).parent

# The cached token at ~/.cache/youtube_publisher/token_677495352.pickle was made
# against this specific client_secret JSON. The auto-picker would otherwise grab
# the alphabetically-first JSON (1013...-MyEmailApp), which is Internal-only and
# rejects markanthonykoop@gmail.com with org_internal.
CLIENT_SECRETS = "/mnt/c/Users/x/Downloads/client_secret_677495352-q1duspp6rlpo0gehpqrlq41rvf08o95f.apps.googleusercontent.com.json"

VIDEOS = [
    ("(Guitar Stem)",  "fog_guitar.mp4"),
    ("(Drums Stem)",   "fog_drums.mp4"),
    ("(Vocals Stem)",  "fog_vocals.mp4"),
    ("(Original Mix)", "fog_original.mp4"),
]

JAM_INVITATION = (
    "This version is easier to play. Anyone that wants to jam it w/ me, "
    "put a link to your channel with your tracks and we can swap files "
    "(or we could get together if you are in Centralish Texas..."
)


def build_description(suffix: str) -> str:
    lines = [
        f"Fog {suffix} — by {ARTIST}",
        f"Released by {LABEL} · {RELEASE_DATE}",
        "",
        JAM_INVITATION,
    ]
    if "(Drums" in suffix:
        lines.append("")
        lines.append("(Drum transcription artifacts pending — basic-pitch is bad at "
                     "drums; ADTOF integration is in progress.)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print planned title+description and exit, no uploads")
    args = ap.parse_args()

    plan = []
    for suffix, mp4_name in VIDEOS:
        title = f"Fog {suffix} — {ARTIST}"
        desc = build_description(suffix)
        plan.append({
            "mp4": str(RUN_DIR / "mp4" / mp4_name),
            "title": title,
            "description": desc,
        })

    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    results = []
    for item in plan:
        print(f"\n→ uploading {item['mp4']}", file=sys.stderr)
        r = upload_video(
            video_path=item["mp4"], title=item["title"],
            description=item["description"],
            tags=["Mark Nadon", "MiddleMatter Music", "Fog", "post punk", "garage", "stems"],
            privacy=PRIVACY_PUBLIC, made_for_kids=False,
            client_secrets_path=CLIENT_SECRETS,
            progress_stream=sys.stderr,
        )
        print(f"  → {r['url']}", file=sys.stderr)
        results.append({"title": item["title"], "url": r["url"], "id": r["video_id"]})
    (RUN_DIR / "youtube_results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
