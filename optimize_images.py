#!/usr/bin/env python3
"""Resize and strip metadata from site photos.

Phone photos land at ~1 MB each, which is far more than a web page needs.
This rewrites everything in docs/assets/img/ to two sizes:

    <name>.jpg        long edge 1600px  — full view / lightbox
    <name>.thumb.jpg  long edge  640px  — card and gallery grid

Originals are copied to originals/photos/ first, so this is non-destructive and safe
to re-run: it only processes files that have no up-to-date output yet.

Usage:
    python3 optimize_images.py            # process new photos
    python3 optimize_images.py --force    # redo everything
"""

import os
import shutil
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "docs", "assets", "img")
ORIG = os.path.join(ROOT, "originals", "photos")

FULL_EDGE = 1600
THUMB_EDGE = 640
QUALITY = 82
SRC_EXT = (".jpg", ".jpeg", ".png", ".webp")
# make_heroes.py owns these; re-encoding its crops here would degrade them
SKIP_DIRS = {"_needs-reupload", "heroes"}
SKIP_FILES = {"headshot.jpg", "headshot.thumb.jpg"}


def save(im, path, edge):
    """Write `im` scaled to fit `edge` on its long side, with no metadata."""
    out = im.copy()
    out.thumbnail((edge, edge), Image.LANCZOS)
    if out.mode not in ("RGB", "L"):
        out = out.convert("RGB")
    # a fresh image carries no EXIF, so nothing to strip explicitly
    out.save(path, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return os.path.getsize(path)


def main():
    force = "--force" in sys.argv
    before = after = 0
    done = skipped = 0

    for dirpath, dirnames, filenames in os.walk(IMG):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            stem, ext = os.path.splitext(name)
            if ext.lower() not in SRC_EXT or stem.endswith(".thumb") \
                    or name in SKIP_FILES:
                continue
            src = os.path.join(dirpath, name)
            full = os.path.join(dirpath, stem + ".jpg")
            thumb = os.path.join(dirpath, stem + ".thumb.jpg")

            if not force and os.path.exists(thumb) and os.path.exists(full) \
                    and os.path.getmtime(thumb) >= os.path.getmtime(src):
                skipped += 1
                continue

            size = os.path.getsize(src)
            try:
                im = ImageOps.exif_transpose(Image.open(src))  # honor rotation
            except Exception as exc:
                print(f"  !! skipping unreadable {src}: {exc}")
                continue

            # keep the untouched original outside the published tree
            rel = os.path.relpath(src, IMG)
            backup = os.path.join(ORIG, rel)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            if not os.path.exists(backup):
                shutil.copy2(src, backup)

            before += size
            after += save(im, full, FULL_EDGE)
            after += save(im, thumb, THUMB_EDGE)
            im.close()

            # drop the source if it was a different extension than our output
            if os.path.abspath(src) != os.path.abspath(full):
                os.remove(src)
            done += 1

    if before:
        print(f"processed {done} photos ({skipped} already current)")
        print(f"  {before/1e6:.1f} MB  ->  {after/1e6:.1f} MB "
              f"({100 - after/before*100:.0f}% smaller, includes thumbnails)")
        print(f"  originals preserved in originals/photos/")
    else:
        print(f"nothing to do ({skipped} photos already current)")


if __name__ == "__main__":
    main()
