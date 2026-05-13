"""Extend YouTube OAuth token with drive.file scope and upload Fog artifacts.

After this runs, the cached token at ~/.cache/youtube_publisher/token_677495352.pickle
has scopes {youtube.upload, drive.file}, so future YouTube uploads keep working AND
Drive uploads work.

Usage:
    python3 upload_to_drive.py

Outputs a JSON map of {filename -> drive_view_url} on stdout, and writes it to
./drive_links.json (next to this script).
"""
import json
import sys
import pickle
from pathlib import Path

import youtube_publisher.auth as ypauth
from youtube_publisher.credentials import pick_client_secrets

SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/drive.file",
)
RUN_DIR = Path(__file__).parent

# If existing token has only youtube scope, blow it away to force fresh consent.
cs = pick_client_secrets()
token_file = ypauth.TOKEN_DIR / f"token_{cs.stem}.pickle"
if token_file.exists():
    with token_file.open("rb") as f:
        creds = pickle.load(f)
    have = set(creds.scopes or [])
    if not set(SCOPES).issubset(have):
        print(f"existing token scopes={have}; need {set(SCOPES)} — re-authing.", file=sys.stderr)
        token_file.unlink()
    else:
        print("existing token already has both scopes; skipping consent.", file=sys.stderr)

creds = ypauth.get_credentials(scopes=SCOPES, open_browser=False)
print(f"creds OK; scopes={list(creds.scopes or [])}", file=sys.stderr)

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

drive = build("drive", "v3", credentials=creds, cache_discovery=False)

FOLDER_NAME = "Fog (2026-05-06) — Stems & Scores"
folder = drive.files().create(
    body={"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
    fields="id, webViewLink",
).execute()
folder_id = folder["id"]
print(f"folder: {folder['webViewLink']}", file=sys.stderr)

# Make folder shareable (anyone with link can view)
drive.permissions().create(
    fileId=folder_id, body={"role": "reader", "type": "anyone"},
).execute()

# Upload artifacts
TRANSCRIBED = Path("/mnt/d/downloads/suno_stems/fog/transcribed")
STEMS_DIR   = Path("/mnt/d/downloads/suno_stems/fog")
files_to_upload: list[Path] = []
for stem in ["fog_guitar", "fog_vocals"]:
    for suffix in [".pdf", ".musicxml", "_basic_pitch.mid", "_notes.tsv", "_summary.json", ".tab"]:
        p = TRANSCRIBED / f"{stem}{suffix}"
        if p.exists():
            files_to_upload.append(p)
files_to_upload.append(STEMS_DIR / "fog_original.mp3")

links: dict[str, str] = {}
for path in files_to_upload:
    media = MediaFileUpload(str(path), resumable=False)
    f = drive.files().create(
        body={"name": path.name, "parents": [folder_id]},
        media_body=media,
        fields="id, webViewLink",
    ).execute()
    links[path.name] = f["webViewLink"]
    print(f"  uploaded {path.name} → {f['webViewLink']}", file=sys.stderr)

result = {"folder_url": folder["webViewLink"], "files": links}
out = RUN_DIR / "drive_links.json"
out.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
