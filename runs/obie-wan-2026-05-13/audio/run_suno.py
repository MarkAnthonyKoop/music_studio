"""Drive Suno: upload Obie's raw guitar, extend with new lyrics, download.

Prereq: Chrome must be closed (so chrome_auth can read the cookie DB) OR a
fresh JWT supplied via $SUNO_JWT.

Reads:
    obie_raw.wav

Writes:
    upload.json            ← clip_id + URL of the uploaded source
    extend.json            ← clip_ids of the two extension candidates
    extended_<id>.mp3      ← the rendered tracks (one per candidate)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/xx/claude")
from suno_client import (
    extend_song,
    get_jwt_from_chrome,
    upload_audio,
    poll_clip,
    download_clip,
)

RUN_DIR = Path(__file__).parent
SOURCE_WAV = RUN_DIR / "obie_raw.wav"

TITLE = "Obie Wan — fog of color"
STYLE_TAGS = (
    "acoustic folk, melancholy, lo-fi, sparse drums, subtle upright bass, "
    "no genre swing, continue the riff"
)
LYRICS = (
    "I don't see red\n"
    "I don't see blue\n"
    "I don't see green, or any hue\n"
    "my world's all gray now\n"
    "now without you\n"
)


def main() -> int:
    if not SOURCE_WAV.exists():
        print(f"missing {SOURCE_WAV}", file=sys.stderr)
        return 1

    jwt = os.environ.get("SUNO_JWT") or get_jwt_from_chrome()
    if not jwt:
        print("ERROR: no Suno JWT. Close Chrome and retry, or set $SUNO_JWT.",
              file=sys.stderr)
        return 2
    print(f"jwt ok ({len(jwt)} chars)")

    # 1. Upload
    upload_json = RUN_DIR / "upload.json"
    if upload_json.exists():
        upload = json.loads(upload_json.read_text())
        print(f"reusing cached upload: {upload['clip_id']}")
    else:
        print("uploading obie_raw.wav (this can take ~30s) ...")
        upload = upload_audio(SOURCE_WAV, jwt)
        upload_json.write_text(json.dumps(upload, indent=2))
        print(f"uploaded: {upload['clip_id']}  url={upload['url']}")

    # 2. Extend
    extend_json = RUN_DIR / "extend.json"
    if extend_json.exists():
        extend = json.loads(extend_json.read_text())
        print(f"reusing cached extend: {extend['clip_ids']}")
    else:
        print("requesting extend ...")
        clip_ids = extend_song(
            jwt=jwt,
            title=TITLE,
            lyrics=LYRICS,
            style_tags=STYLE_TAGS,
            continue_clip_id=upload["clip_id"],
            continue_at=None,  # let Suno pick the join point
        )
        if not clip_ids:
            print("ERROR: extend returned no clip_ids", file=sys.stderr)
            return 3
        extend = {"clip_ids": clip_ids}
        extend_json.write_text(json.dumps(extend, indent=2))
        print(f"extend spawned: {clip_ids}")

    # 3. Poll + download each candidate
    for cid in extend["clip_ids"]:
        out_dir = RUN_DIR / cid
        out_dir.mkdir(exist_ok=True)
        print(f"polling {cid} ...")
        clip = poll_clip(jwt, cid, timeout=600.0)
        paths = download_clip(clip, str(out_dir))
        print(f"  -> {paths}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
