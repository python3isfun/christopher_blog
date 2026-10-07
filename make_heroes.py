#!/usr/bin/env python3
"""Cut hero and card images to fixed aspect ratios from chosen source photos.

Cards and heroes are displayed at a fixed shape, so letting the browser crop
them with object-fit gives up all control over framing — heads get cut off and
the subject drifts out of frame. This crops deliberately instead: pick the
source photo, the target ratio, and where in the frame the subject sits.

Edit HEROES below, then run:

    python3 make_heroes.py

Output lands in docs/assets/img/heroes/ and is referenced from content.json
(a project's "hero" field) or, for the home page, as assets/img/headshot.jpg.
"""

import os

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "docs", "assets", "img")
OUT = os.path.join(IMG, "heroes")

# name -> (source photo under docs/assets/img, width:height, vertical anchor)
# anchor: 0.0 keeps the top of the frame, 0.5 centers, 1.0 keeps the bottom.
# Portraits of people usually want a low number so heads are not cropped.
HEROES = {
    "headshot":        ("anthropomorphic-hand/IMG_7138.jpg", (4, 5), 0.10),
    "big-hands":       ("big-hands/IMG_7537.jpg",            (3, 2), 0.50),
    "shoe-sole":       ("shoe-sole/IMG_1121.jpg",            (3, 2), 0.50),
    "exoskeleton":     ("exoskeleton/IMG_5874.jpg",          (3, 2), 0.30),
    "hand-research":   ("anthropomorphic-hand/IMG_7124.jpg", (3, 2), 0.45),
    "rotary":          ("rotary-competition/IMG_1287.jpg",   (3, 2), 0.20),
}

LONG_EDGE = 1600
THUMB_EDGE = 640
QUALITY = 85


def crop_to_ratio(im, ratio, anchor):
    """Crop `im` to `ratio` (w, h), keeping the band of the image at `anchor`."""
    rw, rh = ratio
    w, h = im.size
    target = rw / rh
    if w / h > target:
        # too wide: trim the sides, always from the centre
        new_w = round(h * target)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        # too tall: trim top/bottom, biased by anchor
        new_h = round(w / target)
        top = round((h - new_h) * anchor)
        box = (0, top, w, top + new_h)
    return im.crop(box)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (src, ratio, anchor) in HEROES.items():
        path = os.path.join(IMG, src)
        if not os.path.exists(path):
            print(f"  !! missing source for {name}: {src}")
            continue
        im = ImageOps.exif_transpose(Image.open(path))
        im = crop_to_ratio(im, ratio, anchor)
        if im.mode != "RGB":
            im = im.convert("RGB")

        full = im.copy()
        full.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        full.save(os.path.join(OUT, name + ".jpg"), "JPEG",
                  quality=QUALITY, optimize=True, progressive=True)

        thumb = im.copy()
        thumb.thumbnail((THUMB_EDGE, THUMB_EDGE), Image.LANCZOS)
        thumb.save(os.path.join(OUT, name + ".thumb.jpg"), "JPEG",
                   quality=QUALITY, optimize=True, progressive=True)

        print(f"  {name:15s} {ratio[0]}:{ratio[1]:<3} {full.size[0]}x{full.size[1]}  <- {src}")
        im.close()

    # the home page picks this up automatically if it exists
    shot = os.path.join(OUT, "headshot.jpg")
    if os.path.exists(shot):
        import shutil
        shutil.copy(shot, os.path.join(IMG, "headshot.jpg"))
        print("\n  copied headshot.jpg into place for the home hero")


if __name__ == "__main__":
    main()
