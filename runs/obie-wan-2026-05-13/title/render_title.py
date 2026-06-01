"""Render a 5-second 'Introducing Obie Wan_' typewriter title card.

Output: title.mp4 at 1080x1920 (portrait, matches the rotated source clip).
"""
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).parent
FRAMES_DIR = OUT_DIR / "frames"
FRAMES_DIR.mkdir(exist_ok=True)
for old in FRAMES_DIR.glob("*.png"):
    old.unlink()

W, H = 1080, 1920
FPS = 30
DURATION_S = 5.0
TYPE_DURATION_S = 2.5   # how long the reveal takes
TEXT = "Introducing Obie Wan"
CURSOR_BLINK_HZ = 2.0    # full on/off cycles per second

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
font_path = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
assert font_path, "No TTF font found"

FONT_SIZE = 78
font = ImageFont.truetype(font_path, FONT_SIZE)

total_frames = int(DURATION_S * FPS)
for i in range(total_frames):
    t = i / FPS
    # How many characters revealed?
    chars = min(len(TEXT), int(len(TEXT) * t / TYPE_DURATION_S))
    revealed = TEXT[:chars]
    # Cursor visibility (blinks). On while typing too.
    cursor_on = (math.floor(t * CURSOR_BLINK_HZ * 2) % 2) == 0
    line = revealed + ("_" if cursor_on else " ")

    img = Image.new("RGB", (W, H), "black")
    draw = ImageDraw.Draw(img)
    # Center: measure once on the *full* text so width doesn't shift
    bbox = draw.textbbox((0, 0), TEXT + "_", font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (W - text_w) // 2
    y = (H - text_h) // 2
    draw.text((x, y), line, fill="white", font=font)
    img.save(FRAMES_DIR / f"f{i:04d}.png")

print(f"Rendered {total_frames} frames -> {FRAMES_DIR}")

# Encode to MP4. Match source's display orientation (portrait 1080x1920).
out_mp4 = OUT_DIR / "title.mp4"
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", str(FRAMES_DIR / "f%04d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
    "-preset", "veryfast",
    str(out_mp4),
]
subprocess.run(cmd, check=True, capture_output=True)
print(f"Wrote {out_mp4}")
