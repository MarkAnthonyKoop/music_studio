"""Per-clip structural analysis to pick the 'best bits'.

For each source clip: tempo, key (Krumhansl chroma match), RMS energy envelope,
and structural section boundaries (librosa agglomerative). Writes one JSON per
clip plus a combined summary, and a per-clip section table to stdout.
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

SRC = Path(__file__).resolve().parent.parent / "src"
OUT = Path(__file__).resolve().parent

KRUMHANSL_MAJ = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KRUMHANSL_MIN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
PITCHES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]


def estimate_key(chroma):
    prof = chroma.mean(axis=1)
    best = (-1, None)
    for i in range(12):
        for prof_t, mode in ((KRUMHANSL_MAJ, "maj"), (KRUMHANSL_MIN, "min")):
            r = np.corrcoef(prof, np.roll(prof_t, i))[0, 1]
            if r > best[0]:
                best = (r, f"{PITCHES[i]} {mode}")
    return best[1], round(float(best[0]), 3)


def analyze(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    dur = len(y) / sr
    tempo = float(librosa.beat.beat_track(y=y, sr=sr)[0])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key, keyconf = estimate_key(chroma)

    # RMS energy envelope, 0.5s frames
    hop = sr // 2
    rms = librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop)[0]
    rms_db = librosa.amplitude_to_db(rms + 1e-6)
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)

    # structural segmentation
    n_seg = max(3, min(8, int(dur // 12)))
    bounds = librosa.segment.agglomerative(chroma, n_seg)
    bt = librosa.frames_to_time(bounds, sr=sr)
    edges = sorted(set([0.0] + [round(float(t), 2) for t in bt] + [round(dur, 2)]))

    sections = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a < 2:
            continue
        m = (times >= a) & (times < b)
        e = float(rms_db[m].mean()) if m.any() else -60.0
        sections.append({"start": round(a, 2), "end": round(b, 2),
                         "dur": round(b - a, 2), "energy_db": round(e, 1)})
    # rank sections by energy
    for rank, s in enumerate(sorted(sections, key=lambda x: -x["energy_db"])):
        s["energy_rank"] = rank + 1

    return {
        "file": Path(path).name, "duration": round(dur, 2),
        "tempo_bpm": round(tempo, 1), "key": key, "key_conf": keyconf,
        "peak_db": round(float(rms_db.max()), 1),
        "mean_db": round(float(rms_db.mean()), 1),
        "sections": sections,
    }


def main():
    results = []
    for p in sorted(SRC.glob("clip*.mp3")):
        r = analyze(str(p))
        results.append(r)
        (OUT / f"{p.stem}.json").write_text(json.dumps(r, indent=2))
        print(f"\n### {r['file']}  {r['duration']}s  {r['tempo_bpm']}bpm  "
              f"key={r['key']}({r['key_conf']})  peak={r['peak_db']}dB")
        for s in r["sections"]:
            bar = "#" * int(max(0, s["energy_db"] + 60) / 3)
            print(f"  {s['start']:6.1f}-{s['end']:6.1f}s "
                  f"({s['dur']:4.1f}s) {s['energy_db']:6.1f}dB "
                  f"rank{s['energy_rank']} {bar}")
    (OUT / "summary.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {OUT}/summary.json")


if __name__ == "__main__":
    main()
