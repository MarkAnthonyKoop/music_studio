"""Compose final 1920x1080 cover JPEGs from the AI base + title overlay.

Layout: blurred-stretched AI image as widescreen background, sharp 1080x1080
center crop on top. Title and subtitle sit in the left blurred wing so they
don't fight the AI image's subject.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CENTER = 1080
W, H = 1920, 1080
WING = (W - CENTER) // 2

TITLE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SUB_FONT   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

STEMS = [
    ("original", "fog", "Mark Nadon", "MiddleMatter Music"),
    ("guitar",   "fog", "guitar stem", "Mark Nadon"),
    ("drums",    "fog", "drums stem", "Mark Nadon"),
    ("vocals",   "fog", "vocals stem", "Mark Nadon"),
]

run_dir = Path(__file__).parent
src_dir = run_dir / "ai_covers_v2"
out_dir = run_dir / "composed_covers"
out_dir.mkdir(parents=True, exist_ok=True)

for stem, title, sub_a, sub_b in STEMS:
    src = src_dir / f"{stem}.jpg"
    if not src.exists():
        print(f"SKIP {stem}: {src} missing")
        continue
    ai = Image.open(src).convert("RGB")

    bg = ai.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=55))
    bg = bg.point(lambda p: int(p * 0.55))

    center = ai.resize((CENTER, CENTER), Image.LANCZOS)
    bg.paste(center, (WING, (H - CENTER) // 2))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = ImageFont.truetype(TITLE_FONT, 200)
    sub_font   = ImageFont.truetype(SUB_FONT, 34)

    cx = WING // 2
    draw.text((cx, H // 2 - 40), title,
              fill=(230, 240, 250, 230), anchor="mm", font=title_font)
    draw.text((cx, H // 2 + 110), sub_a,
              fill=(210, 220, 235, 200), anchor="mm", font=sub_font)
    draw.text((cx, H // 2 + 155), sub_b,
              fill=(210, 220, 235, 200), anchor="mm", font=sub_font)

    final = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    out = out_dir / f"cover_{stem}.jpg"
    final.save(out, quality=92, optimize=True)
    print(f"wrote {out}")
