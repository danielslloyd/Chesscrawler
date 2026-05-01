"""Generate 32x32 placeholder PNG sprites for Chess Dungeon Crawler.

Run from the repo root:  python3 tools/gen_placeholder_sprites.py

Each sprite is a flat colored 32x32 tile with a single glyph centered on it.
These are intentionally simple — replace them with real pixel art whenever.
The game falls back to drawn glyphs if any PNG is missing.
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

TILE = 32
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


SPRITES = {
    # terrain
    "floor":       {"bg": (60, 70, 90),   "fg": (90, 100, 120), "glyph": "·"},
    "floor_alt":   {"bg": (50, 60, 80),   "fg": (90, 100, 120), "glyph": "·"},
    "wall":        {"bg": (74, 85, 104),  "fg": (40, 45, 55),   "glyph": "#"},
    "door":        {"bg": (139, 92, 51),  "fg": (60, 35, 15),   "glyph": "+"},
    "locked_door": {"bg": (160, 82, 45),  "fg": (220, 180, 40), "glyph": "L"},
    "stairs":      {"bg": (40, 70, 100),  "fg": (200, 220, 255),"glyph": ">"},
    # items
    "key":         {"bg": (60, 70, 90),   "fg": (255, 215, 0),  "glyph": "k"},
    "loot":        {"bg": (60, 70, 90),   "fg": (255, 215, 0),  "glyph": "$"},
    "powerup":     {"bg": (60, 70, 90),   "fg": (147, 200, 255),"glyph": "*"},
    "portal":      {"bg": (75, 0, 130),   "fg": (200, 100, 255),"glyph": "O"},
    # party
    "wizard":      {"bg": (45, 30, 90),   "fg": (200, 180, 255),"glyph": "B"},  # bishop
    "warrior":     {"bg": (90, 30, 30),   "fg": (255, 200, 200),"glyph": "R"},  # rook
    "thief":       {"bg": (30, 60, 30),   "fg": (180, 255, 180),"glyph": "N"},  # knight
    "healer":      {"bg": (90, 30, 90),   "fg": (255, 220, 255),"glyph": "Q"},  # queen
    "assassin":    {"bg": (30, 30, 30),   "fg": (220, 220, 220),"glyph": "P"},  # pawn
    "paladin":     {"bg": (90, 90, 30),   "fg": (255, 255, 200),"glyph": "K"},  # king
    # enemies
    "goblin":      {"bg": (30, 70, 30),   "fg": (180, 255, 100),"glyph": "g"},
    "spider":      {"bg": (30, 30, 60),   "fg": (200, 100, 255),"glyph": "s"},
    "boss":        {"bg": (90, 0, 0),     "fg": (255, 100, 100),"glyph": "X"},
    # ui
    "spawn":       {"bg": (40, 40, 40),   "fg": (100, 255, 100),"glyph": "@"},
}


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_sprite(name: str, spec: dict) -> Image.Image:
    img = Image.new("RGBA", (TILE, TILE), spec["bg"] + (255,))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([0, 0, TILE - 1, TILE - 1], outline=(0, 0, 0, 180), width=1)

    # Inner accent: small inset rect for depth
    draw.rectangle([2, 2, TILE - 3, TILE - 3],
                   outline=tuple(min(255, c + 25) for c in spec["bg"]) + (200,),
                   width=1)

    # Glyph
    glyph = spec["glyph"]
    font = find_font(20)
    bbox = draw.textbbox((0, 0), glyph, font=font)
    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]
    draw.text(
        ((TILE - gw) // 2 - bbox[0], (TILE - gh) // 2 - bbox[1]),
        glyph,
        fill=spec["fg"] + (255,),
        font=font,
    )
    return img


def main() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for name, spec in SPRITES.items():
        path = os.path.join(ASSETS_DIR, f"{name}.png")
        img = make_sprite(name, spec)
        img.save(path, "PNG")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
