from __future__ import annotations

"""
Image enhancement + composite CLI

- Enhances two input images (a human face photo and a cartoon poop with flies)
- Composites them into a single square (1:1) image at the desired resolution
- Layout (default):
  - Face in the foreground
  - Poop centered and wrapping around the face via a soft cut-out ring
  - Flies kept at roughly their original relative positions (auto-detected)
  - Slight warm tone and stronger contrast for a realistic style

Usage example:

  python -m backend.app.utils.compose_face_poop \
      --face /path/to/face.jpg \
      --poop /path/to/poop.png \
      --out /path/to/output.png \
      --size 1080

This script only depends on Pillow (already in requirements).
"""

import argparse
import math
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops, ImageDraw


@dataclass
class FlyPoint:
    x_norm: float  # normalized [0,1] in poop image space width
    y_norm: float  # normalized [0,1] in poop image space height
    strength: float  # detection confidence (used for sizing)


# -----------------------------
# Generic image utilities
# -----------------------------

def load_image_rgba(path: str) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    return img


def enhance_image(
    img: Image.Image,
    target_min_side: int | None = None,
    denoise: bool = True,
    contrast: float = 1.18,
    sharpness: float = 1.6,
    color: float = 1.08,
    warmth: float = 0.08,
) -> Image.Image:
    """Apply light denoise, contrast, sharpness and a warm tone.

    warmth: 0..1, roughly adds red and reduces blue slightly
    """
    if target_min_side is not None:
        w, h = img.size
        scale = max(1.0, target_min_side / float(min(w, h)))
        if scale > 1.01:
            img = img.resize((int(round(w * scale)), int(round(h * scale))), Image.Resampling.LANCZOS)

    if denoise:
        img = img.filter(ImageFilter.MedianFilter(size=3))

    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(color)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    # Warm tone by channel adjustment (no numpy)
    r, g, b, a = img.split()
    def point_scale(ch: Image.Image, add: int = 0, mul: float = 1.0) -> Image.Image:
        table = [max(0, min(255, int(add + mul * i))) for i in range(256)]
        return ch.point(table)

    warm_add = int(255 * (warmth * 0.06))
    cool_sub = int(255 * (warmth * 0.06))
    r = point_scale(r, add=warm_add, mul=1.0)
    b = point_scale(b, add=-cool_sub, mul=1.0)
    img = Image.merge("RGBA", (r, g, b, a))

    return img


def fit_into_square(img: Image.Image, size: int) -> Image.Image:
    """Letterbox an image into a square canvas with transparent background."""
    w, h = img.size
    scale = min(size / w, size / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.alpha_composite(img_resized, (x, y))
    return canvas


# -----------------------------
# Flies detection and drawing
# -----------------------------

def detect_fly_points(poop_rgba: Image.Image, max_points: int = 3) -> List[FlyPoint]:
    """Detect likely fly positions by finding cyan/white wing clusters.

    Heuristic: wings are light with stronger G and B than R (cyan-ish).
    We bucket pixels into a coarse grid and pick top clusters.
    """
    img = poop_rgba.convert("RGB")
    w, h = img.size
    pixels = img.load()

    cell = max(12, min(w, h) // 24)  # grid size
    cols = max(1, w // cell)
    rows = max(1, h // cell)
    buckets = [[0 for _ in range(cols)] for _ in range(rows)]

    for yy in range(h):
        for xx in range(w):
            r, g, b = pixels[xx, yy]
            # cyan/white wing heuristic
            if g > 140 and b > 140 and r < 160 and (g + b) - r > 120:
                by = min(rows - 1, yy // cell)
                bx = min(cols - 1, xx // cell)
                buckets[by][bx] += 1

    # collect top buckets
    scored: List[Tuple[int, int, int]] = []  # (count, bx, by)
    for by in range(rows):
        for bx in range(cols):
            cnt = buckets[by][bx]
            if cnt > 0:
                scored.append((cnt, bx, by))

    scored.sort(reverse=True, key=lambda t: t[0])
    top = scored[:max_points]

    # convert to normalized points at cell centers
    points: List[FlyPoint] = []
    for cnt, bx, by in top:
        cx = (bx + 0.5) * cell
        cy = (by + 0.5) * cell
        points.append(FlyPoint(x_norm=cx / w, y_norm=cy / h, strength=min(1.0, cnt / (cell * cell * 0.6))))

    # Fallback default positions if none detected
    if not points:
        points = [
            FlyPoint(0.28, 0.18, 0.7),
            FlyPoint(0.52, 0.12, 0.7),
            FlyPoint(0.74, 0.20, 0.7),
        ]
    return points


def create_fly_sprite(base_size: int = 64) -> Image.Image:
    """Create a simple 3D-looking fly sprite (RGBA)."""
    size = max(16, base_size)
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(sprite)

    # Drop shadow
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    ds.ellipse([size * 0.18, size * 0.60, size * 0.82, size * 0.92], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=size * 0.08))
    sprite.alpha_composite(shadow, (0, 0))

    # Body
    body_bbox = [size * 0.30, size * 0.30, size * 0.70, size * 0.80]
    d.ellipse(body_bbox, fill=(20, 20, 20, 255))
    # Head
    d.ellipse([size * 0.40, size * 0.20, size * 0.60, size * 0.40], fill=(10, 10, 10, 255))

    # Wings (slightly translucent cyan-white)
    wing_color = (200, 235, 245, 200)
    d.ellipse([size * 0.18, size * 0.05, size * 0.52, size * 0.45], fill=wing_color)
    d.ellipse([size * 0.48, size * 0.05, size * 0.82, size * 0.45], fill=wing_color)

    # Highlights
    d.ellipse([size * 0.40, size * 0.36, size * 0.55, size * 0.48], fill=(255, 255, 255, 50))

    return sprite


# -----------------------------
# Compositing helpers
# -----------------------------

def create_soft_hole_mask(size: int, hole_ratio: float = 0.48, feather: int = 28) -> Image.Image:
    """Create a full-opaque mask with a soft transparent ellipse in the center."""
    mask = Image.new("L", (size, size), 255)
    d = ImageDraw.Draw(mask)
    margin = int(size * (1.0 - hole_ratio))
    bbox = [margin, margin, size - margin, size - margin]
    d.ellipse(bbox, fill=0)
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
    return mask


def create_soft_ellipse_mask(size: int, ratio: float = 0.60, feather: int = 22) -> Image.Image:
    """A soft elliptical mask (opaque inside, transparent outside)."""
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    margin = int(size * (1.0 - ratio))
    bbox = [margin, int(margin * 0.8), size - margin, size - int(margin * 1.2)]
    d.ellipse(bbox, fill=255)
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))
    return mask


def keep_alpha(img: Image.Image) -> Image.Image:
    return img if img.mode == "RGBA" else img.convert("RGBA")


# -----------------------------
# Main composition pipeline
# -----------------------------

def compose(
    face_path: str,
    poop_path: str,
    out_path: str,
    size: int = 1080,
    warm_contrast_final: float = 1.06,
) -> None:
    # Load and enhance inputs
    face = load_image_rgba(face_path)
    poop = load_image_rgba(poop_path)

    face = enhance_image(face, target_min_side=1024, denoise=True)
    poop = enhance_image(poop, target_min_side=1024, denoise=False, contrast=1.12, sharpness=1.2, color=1.02)

    # Prepare square canvases
    face_sq = fit_into_square(face, size)
    poop_sq = fit_into_square(poop, size)

    # Build base canvas with subtle warm tone background
    canvas = Image.new("RGBA", (size, size), (245, 238, 230, 255))

    # Poop ring with cut-out hole
    hole_mask = create_soft_hole_mask(size, hole_ratio=0.50, feather=max(10, size // 48))
    poop_ring = keep_alpha(poop_sq)
    poop_ring.putalpha(ImageChops.multiply(poop_ring.split()[-1], hole_mask))

    # Face with soft elliptical edge to emphasize features in the foreground
    face_mask = create_soft_ellipse_mask(size, ratio=0.68, feather=max(14, size // 60))
    face_fg = keep_alpha(face_sq)
    face_fg.putalpha(face_mask)

    # Light shadow ring over the face for depth
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sh = ImageDraw.Draw(shadow)
    sh_margin = int(size * 0.14)
    sh_bbox_outer = [sh_margin, sh_margin, size - sh_margin, size - sh_margin]
    sh_bbox_inner = [sh_margin + int(size * 0.06), sh_margin + int(size * 0.06), size - sh_margin - int(size * 0.06), size - sh_margin - int(size * 0.06)]
    sh.ellipse(sh_bbox_outer, fill=(0, 0, 0, 80))
    sh.ellipse(sh_bbox_inner, fill=(0, 0, 0, 0))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(8, size // 50)))

    # Composite order: background -> poop ring (behind) -> face foreground -> subtle shadow from ring -> flies
    canvas.alpha_composite(poop_ring)
    canvas.alpha_composite(face_fg)
    canvas.alpha_composite(shadow)

    # Detect and render flies roughly at original positions
    fly_points = detect_fly_points(poop, max_points=3)

    for fp in fly_points:
        # Fly size scales with confidence and canvas size
        fly_size = int(max(size * 0.07, size * 0.07 * fp.strength))
        fly_sprite = create_fly_sprite(fly_size)

        # Map normalized coords from original poop image to the fitted poop canvas placement
        # Our poop_sq is centered and scaled; since both are square-fit, mapping is nearly identity
        cx = int(fp.x_norm * size)
        cy = int(fp.y_norm * size)

        # Offset to place the fly above the ring with a hint of 3D (raise slightly)
        pos = (cx - fly_size // 2, cy - fly_size // 2 - int(size * 0.02))
        canvas.alpha_composite(fly_sprite, dest=pos)

    # Final small contrast/warm tweak for coherence
    final = ImageEnhance.Contrast(canvas).enhance(warm_contrast_final)
    final = ImageEnhance.Color(final).enhance(1.04)

    final.save(out_path)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Enhance two images and composite into a realistic 1:1 artwork.")
    p.add_argument("--face", required=True, help="Path to the face image")
    p.add_argument("--poop", required=True, help="Path to the poop-with-flies image")
    p.add_argument("--out", required=True, help="Output image path (PNG recommended)")
    p.add_argument("--size", type=int, default=1080, help="Output square size in pixels (default: 1080)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    compose(face_path=args.face, poop_path=args.poop, out_path=args.out, size=args.size)


if __name__ == "__main__":
    main()
