"""Comp the best bits of the two sibling 3:57pm takes (B + C) into one arc.

Sequence with equal-power crossfades, then EBU R128 loudness-normalize via ffmpeg.
Editorial choices come from analysis/summary.json (energy rank + structure).
clipA is intentionally excluded from the body (161bpm/major clashes with the
~115bpm minor body); it's rendered as a standalone option instead.
"""
import subprocess
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

RUN = Path(__file__).resolve().parent.parent
SRC = RUN / "src"
OUT = RUN / "out"
SR = 44100
XF = 0.6  # crossfade seconds

# (file, start_s, end_s, note)
ARRANGEMENT = [
    ("clipC_357pm_121s.mp3", 0.0, 13.2, "Gmin intro / mood"),
    ("clipC_357pm_121s.mp3", 16.1, 41.3, "Gmin main groove"),
    ("clipB_357pm_113s.mp3", 17.5, 36.9, "A#min build -> peak/drop (key lift)"),
    ("clipC_357pm_121s.mp3", 81.6, 88.5, "Gmin punch hook"),
    ("clipB_357pm_113s.mp3", 97.8, 113.5, "A#min resolve / outro"),
]

_cache = {}


def load(name):
    if name not in _cache:
        y, _ = librosa.load(str(SRC / name), sr=SR, mono=False)
        if y.ndim == 1:
            y = np.stack([y, y])
        _cache[name] = y
    return _cache[name]


def seg(name, a, b):
    y = load(name)
    return y[:, int(a * SR):int(b * SR)]


def xfade(prev, nxt, n):
    """Equal-power crossfade: blend last n samples of prev with first n of nxt."""
    if prev.shape[1] < n or nxt.shape[1] < n:
        return np.concatenate([prev, nxt], axis=1)
    t = np.linspace(0, np.pi / 2, n)
    fo, fi = np.cos(t), np.sin(t)
    head, tail = prev[:, :-n], prev[:, -n:]
    blend = tail * fo + nxt[:, :n] * fi
    return np.concatenate([head, blend, nxt[:, n:]], axis=1)


def build(segments, xf=XF):
    n = int(xf * SR)
    out = None
    for s in segments:
        out = s if out is None else xfade(out, s, n)
    # short fade in/out to avoid clicks
    f = int(0.04 * SR)
    ramp = np.linspace(0, 1, f)
    out[:, :f] *= ramp
    out[:, -f:] *= ramp[::-1]
    return out


def loudnorm(wav_in, mp3_out):
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_in),
         "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
         "-c:a", "libmp3lame", "-q:a", "2", str(mp3_out)],
        check=True, capture_output=True)


def main():
    segs = [seg(*a[:3]) for a in ARRANGEMENT]
    comp = build(segs)
    dur = comp.shape[1] / SR
    wav = OUT / "comp_BC.wav"
    sf.write(str(wav), comp.T, SR)
    loudnorm(wav, OUT / "comp_BC.mp3")
    print(f"comp_BC: {dur:.1f}s, {len(ARRANGEMENT)} sections")
    for f, a, b, note in ARRANGEMENT:
        print(f"  {f[:5]} {a:5.1f}-{b:5.1f}  {note}")

    # standalone option: clipA's bright climax (its rank-1 section + tail)
    a_seg = build([seg("clipA_0735am_51s.mp3", 18.5, 51.5)])
    sf.write(str(OUT / "optA.wav"), a_seg.T, SR)
    loudnorm(OUT / "optA.wav", OUT / "optA.mp3")
    print(f"optA: {a_seg.shape[1]/SR:.1f}s (clipA bright climax, held out of comp)")


if __name__ == "__main__":
    main()
