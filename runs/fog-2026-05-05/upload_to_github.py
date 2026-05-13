"""Upload Fog transcribed artifacts to a GitHub repo via the Contents API.

Reads PAT from ~/.git-credentials. Targets a repo whose name is passed via
--repo (default middlematter-releases). Files land at <repo>/fog/<filename>
on the default branch. Writes ./github_links.json mapping filename → raw URL,
which upload_to_youtube_descriptions.py then splices into descriptions.

Usage:
    python3 upload_to_github.py [--repo middlematter-releases] [--user MarkAnthonyKoop]
"""
import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RUN_DIR = Path(__file__).parent
TRANSCRIBED = Path("/mnt/d/downloads/suno_stems/fog/transcribed")
STEMS_DIR   = Path("/mnt/d/downloads/suno_stems/fog")

# Per-stem files mirrored from the original upload_to_drive.py (no bass).
STEMS = ["fog_guitar", "fog_vocals"]
SUFFIXES = [".pdf", ".musicxml", "_basic_pitch.mid", "_notes.tsv", "_summary.json", ".tab"]


def pat_from_credstore() -> str:
    creds = Path.home() / ".git-credentials"
    for line in creds.read_text().splitlines():
        m = re.match(r"https://[^:]+:([^@]+)@github\.com", line)
        if m:
            return m.group(1)
    raise SystemExit("no github PAT found in ~/.git-credentials")


def gh(method: str, path: str, pat: str, body: dict | None = None) -> dict:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    })
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code} {e.read().decode()}")


def ensure_repo(user: str, repo: str, pat: str) -> str:
    """Return the default branch name. Creates the repo if missing."""
    try:
        info = gh("GET", f"/repos/{user}/{repo}", pat)
        return info["default_branch"]
    except SystemExit as e:
        if "404" not in str(e):
            raise
    info = gh("POST", "/user/repos", pat, {
        "name": repo, "private": False, "auto_init": True,
        "description": "Stems, scores, and source artifacts for MiddleMatter Music releases (Mark Nadon).",
        "homepage": "https://www.youtube.com/@MarkNadon",
        "license_template": "cc-by-4.0",
    })
    return info["default_branch"]


def put_file(user: str, repo: str, path_in_repo: str, content: bytes,
             pat: str, message: str) -> str:
    """Create or update one file. Returns the raw.githubusercontent.com URL."""
    api_path = f"/repos/{user}/{repo}/contents/{path_in_repo}"
    body = {"message": message, "content": base64.b64encode(content).decode()}
    try:
        existing = gh("GET", api_path, pat)
        body["sha"] = existing["sha"]
    except SystemExit:
        pass
    gh("PUT", api_path, pat, body)
    return f"https://raw.githubusercontent.com/{user}/{repo}/HEAD/{path_in_repo}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="MarkAnthonyKoop")
    ap.add_argument("--repo", default="middlematter-releases")
    args = ap.parse_args()
    pat = pat_from_credstore()

    ensure_repo(args.user, args.repo, pat)

    files: list[Path] = []
    for stem in STEMS:
        for suf in SUFFIXES:
            p = TRANSCRIBED / f"{stem}{suf}"
            if p.exists():
                files.append(p)
    files.append(STEMS_DIR / "fog_original.mp3")

    links: dict[str, str] = {}
    for p in files:
        url = put_file(args.user, args.repo, f"fog/{p.name}",
                       p.read_bytes(), pat, f"Add {p.name}")
        links[p.name] = url
        print(f"  {p.name:35} -> {url}", file=sys.stderr)

    repo_url = f"https://github.com/{args.user}/{args.repo}/tree/HEAD/fog"
    out = {"repo_url": repo_url, "files": links}
    (RUN_DIR / "github_links.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
